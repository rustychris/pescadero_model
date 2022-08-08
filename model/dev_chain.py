import stompy.model.delft.dflow_model as dfm
import stompy.model.delft.io as dio
from stompy import utils


run_dir="data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00"

mod=dfm.DFlowModel.load(run_dir)

##

@utils.add_to(mod)
def chain_restarts(self):
    # eventually support criteria on how far back
    # returns a list of MDU objects (with .filename set),
    # including self.mdu
    mdus=[self.mdu]

    mdu=self.mdu
    
    while 1:
        if not mdu['restart','RestartFile']:
            break
        restart=mdu['restart','RestartFile']
        # '../data_2016long_3d_asbuilt_impaired_scen2_l100-v007/DFM_OUTPUT_flowfm/flowfm_20160711_000000_rst.nc'
        # For now, this only works if the paths are 'normal'
        restart_mdu=os.path.dirname(restart).replace('DFM_OUTPUT_','')+".mdu"
        restart_mdu=os.path.normpath( os.path.join(os.path.dirname(mdu.filename),restart_mdu) )
        if not os.path.exists(restart_mdu):
            self.log.warning("Expected preceding restart at %s, but not there"%restart_mdu)
            break
        mdu=dio.MDUFile(restart_mdu)
        mdus.insert(0,mdu)
    return mdus

mdus=mod.chain_restarts()
