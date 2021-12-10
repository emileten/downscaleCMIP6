import papermill as pm


gcm = 'CAMS-CSM1-0'
ssp = 'ssp370'
params = dict(gcm=gcm, ssp=ssp)
output = f'/home/jovyan/output/global_validation_tasmax_automated_{gcm}_{ssp}.ipynb'
pm.execute_notebook(
   '/home/jovyan/repositories/downscaleCMIP6/notebooks/downscaling_pipeline/global_validation_manual.ipynb',
   output,
   parameters=params
)

