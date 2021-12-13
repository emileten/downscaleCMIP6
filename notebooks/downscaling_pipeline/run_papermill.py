# import sys
# import papermill as pm
# import models_QC 
# import rhg_compute_tools.kubernetes as rhgk
# client, cluster = rhgk.get_standard_cluster()
# print(cluster)
# print(cluster.dashboard_link)
# cluster.adapt(minimum=0, maximum=150)
# models = models_QC.QC_models_dict()

# for model_name in models:
#     params = dict(gcm=model_name, argo_token=sys.argv[1])
#     output = f'/home/jovyan/output/global_validation_tasmax_automated_{model_name}_ssp370.ipynb'
#     try:
#         pm.execute_notebook(
#            '/home/jovyan/repositories/downscaleCMIP6/notebooks/downscaling_pipeline/global_validation_manual.ipynb',
#            output,
#            parameters=params
#         )
#     except KeyboardInterrupt:
#         print('shutting down')
#         client.restart() 
#         #cluster.scale(0)
#         client.close()
#         cluster.close()
#     except Exception: 
#         print(f'I could not process {model_name}, proceeding with next')
#         pass

# client.restart() 
# #cluster.scale(0)
# client.close()
# cluster.close()

import papermill as pm
import rhg_compute_tools.kubernetes as rhgk
client, cluster = rhgk.get_standard_cluster()
print(cluster)
print(cluster.dashboard_link)
pm.execute_notebook(
   '/home/jovyan/repositories/downscaleCMIP6/notebooks/downscaling_pipeline/Untitled.ipynb',
   '/home/jovyan/repositories/downscaleCMIP6/notebooks/downscaling_pipeline/Untitled_run.ipynb',
   parameters={'cluster':cluster, 'client':client}
)
    

client.restart() 
#cluster.scale(0)
client.close()
cluster.close()