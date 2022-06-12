# First, hard code one.

import stompy.model.delft.dflow_model as dfm
import xarray as xr
import numpy as np
import logging

import local_config
class PescaRestart(local_config.LocalConfig,dfm.DFlowModel):
    pass


log=logging.getLogger()


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description='Restart Pescadero hydro model for high resolution output.')
    parser.add_argument('--mdu',help='Path to MDU file when run as BMI task')
    parser.add_argument('--start',help='Date/time for restart, YYYY-MM-DDTHH:MM')
    parser.add_argument('--duration',help='Duration of run, <nnnn>[hD]',default='36h')
    parser.add_argument('--suffix',help='suffix for the new, shallow restart',default='r000')
    parser.add_argument('--dryrun',help="Don't actually start simulation",action='store_true')
    
    args = parser.parse_args(argv)

    old_model=PescaRestart.load(args.mdu)
    model=old_model.create_restart(deep=False,mdu_suffix=args.suffix)

    model.run_start=np.datetime64(args.start)

    duration=np.timedelta64(int(args.duration[:-1]), args.duration[-1])
    model.run_stop=model.run_start + duration
    
    # Alter settings as needed
    # For now assume we want roughly "full" output
    model.mdu['output','mapinterval'] = 6*60 # 6 minutes
    # model.mdu['output','Wrimap_velocity_vector'] = 1
    # model.mdu['output','Wrimap_turbulence']=1
    model.mdu['time','TimeStepAnalysis']=1
    model.mdu['output','Wrimap_volume1']=1
    model.mdu['output','Wrimap_flow_analysis']=1 # is this real?

    model.update_config()
    model.mdu.write()
    model.partition()

    if not args.dryrun:
        try:
            model.run_simulation()
        except Exception as exc:
            log.error("run_simulation failed",exc_info=True)
    return model
 
if __name__=='__main__':
    main()

