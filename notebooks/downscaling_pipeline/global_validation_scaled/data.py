import xarray as xr
import gcsfs
import re
import requests
import json


def get_output_path(manifest, regex):
    """
    lists status.nodes in an argo manifest, and grabs intermediary output files paths using the node tree represented by
    status.nodes[*].name. Keeps only nodes of type 'Pod' and phase 'succeeded'.

    Parameters
    ----------
    manifest : dict
    regex : str
        regular expression syntax str to filter nodes based on which templates were executed within a given node and before that given
        node in the tree.
    Returns
    ------
    dict:
        path : str, the path to the intermediary output file
        nodeId: the id of the manifest node that outputted this file
    """
    out_zarr_path = None
    nodeId = None
    i = 0

    for node in manifest["status"]["nodes"]:
        this_node = manifest["status"]["nodes"][node]
        if (
            this_node["type"] == "Pod"
            and this_node["phase"] == "Succeeded"
            and re.search(regex, this_node["name"])
        ):
            i = i + 1
            if i > 1:
                raise Exception(
                    "I could not identify a unique node in the manifest for regex : "
                    + regex
                    + "\n"
                    + ". Id of the first match : "
                    + nodeId
                    + "\n"
                    + "Id of second match : "
                    + this_node["id"]
                )
            nodeId = this_node["id"]
            if "outputs" in this_node and "parameters" in this_node["outputs"]:
                for param in this_node["outputs"]["parameters"]:
                    if param["name"] == "out-zarr":
                        out_zarr_path = param["value"]

    if out_zarr_path is None and nodeId is None:
        raise Exception("I could not identify any node in the manifest")

    return {"path": out_zarr_path, "nodeId": nodeId}


def get_manifest(
    workflow_identifier,
    auth_token,
    argo_url="https://argo.cildc6.org/api/v1",
    workflow_location="workflows",
    namespace="default",
):
    """
    make an http request to retrieve a workflow manifest from an argo server

    Parameters
    ----------
    workflow_uid: str
        unique workflow identifier
    auth_token: str
        argo server authentication
    argo_url: str
        url of argo server
    workflow_location: str
       'workflows' or 'archived-workflows'
    namespace: str
        argo namespace, ignored for archive.
    Returns
    -------
    dict
        representation of the workflow manifest in dict format parsed form json file
    """
    if workflow_location == "workflows":
        return requests.get(
            url=f"{argo_url}/{workflow_location}/{namespace}/" + workflow_identifier,
            headers={"Authorization": auth_token},
        ).json()
    elif workflow_location == "archived-workflows":
        return requests.get(
            url=f"{argo_url}/{workflow_location}/{workflow_identifier}",
            headers={"Authorization": auth_token},
        ).json()


def collect_paths(manifest, gcm="GFDL-ESM4", ssp="ssp370", var="tasmax"):
    """
    collect intermediary output file paths to be validated from an argo manifest : CMIP6, ERA-5, bias corrected, and downscaled output
    data, both in low and high resolution. Depends on a precise version of the workflow template names.

    Parameters
    ---------
    manifest: dict
    gcm: str
    ssp: str
    var: str

    Returns
    -------
    dict
    """

    future_token = "(?=.*,target:ssp,)"
    historical_token = "(?=.*,target:historical,)"
    var_token = f'(?=.*"variable_id":"{var}")'
    ssp_token = f'(?=.*"experiment_id":"{ssp}")'
    gcm_token = f'(?=.*"source_id":"{gcm}")'
    f = get_output_path

    # not looping for this because of the ERA idiosyncratic case
    data_dict = {
        "coarse": {
            "cmip6": {
                ssp: f(
                    manifest,
                    f"{future_token}{var_token}{ssp_token}{gcm_token}(?=.*biascorrect)(?=.*preprocess-simulation)",
                )["path"],
                "historical": f(
                    manifest,
                    f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*biascorrect)(?=.*preprocess-simulation)",
                )["path"],
            },
            "bias_corrected": {
                ssp: f(
                    manifest,
                    f"{future_token}{var_token}{ssp_token}{gcm_token}(?=.*rechunk-biascorrected)",
                )["path"],
                "historical": f(
                    manifest,
                    f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*rechunk-biascorrected)",
                )["path"],
            },
            "ERA-5": f(
                manifest,
                f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*biascorrect)(?=.*preprocess-reference)",
            )["path"],
        },
        "fine": {
            "bias_corrected": {
                ssp: f(
                    manifest,
                    f"{future_token}{var_token}{ssp_token}{gcm_token}(?=.*preprocess-biascorrected)(?=.*regrid)(?=.*prime-regrid-zarr)",
                )["path"],
                "historical": f(
                    manifest,
                    f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*preprocess-biascorrected)(?=.*regrid)(?=.*prime-regrid-zarr)",
                )["path"],
            },
            "downscaled": {
                ssp: f(
                    manifest,
                    f"{future_token}{var_token}{ssp_token}{gcm_token}(?=.*prime-qplad-output-zarr)",
                )["path"],
                "historical": f(
                    manifest,
                    f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*prime-qplad-output-zarr)",
                )["path"],
            },
            "ERA-5_fine": f(
                manifest,
                f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*create-fine-reference)(?=.*move-chunks-to-space)",
            )["path"],
            "ERA-5_coarse": f(
                manifest,
                f"{historical_token}{var_token}{ssp_token}{gcm_token}(?=.*create-coarse-reference)(?=.*move-chunks-to-space)",
            )["path"],
        },
    }

    return data_dict


def build_data_paths_dict(infile, outfile, var, ssp, argo_token):
    """
    Takes a json containing variable-ssp-gcm-workflow ids, picks one variable-ssp,
    and retrieves and parses worfklow manifests associated with each gcm, storing data paths.
    Writes another json with the latter.

    Parameters
    ----------
    in: str
        path to json
    out: str
        path to json
    gcm: str
    var: str
    argo_token: str
    """

    results = {}
    with open(infile, "r") as inputfile:
        ids = json.loads(inputfile)
    if var not in ids:
        raise ValueError("no workflow uids for this variable")
    ids = ids[var]

    for gcm, workflow in ids.items():
        print(f"retrieving {gcm}")
        workflow_location = "archived-workflows"
        manifest = get_manifest(
            workflow_identifier=workflow,
            auth_token=argo_token,
            workflow_location=workflow_location,
        )
        results[gcm] = collect_paths(manifest, gcm, ssp, var)

    with open(outfile, "w") as outputfile:
        json.dump(results, outputfile)

