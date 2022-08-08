# First, hard code one.

import stompy.model.delft.dflow_model as dfm
import os, shutil
import xarray as xr
import numpy as np
import logging

import local_config
class PescaRestart(local_config.LocalConfig,dfm.DFlowModel):
    def create_restart(self,deep=True,mdu_suffix="",**kwargs):
        # Skip configure as we want to preserve as much of the original run as possible.
        new_model=self.__class__(configure=False,**kwargs) # in case of subclassing, rather than DFlowModel()
        new_model.set_restart_from(self,deep=deep,mdu_suffix=mdu_suffix)
        return new_model
    
    def write(self):
        # Code this as if it could be for DFlowModel.write()
        if not bool(self.restart):
            super().write()
        else:
            if self.restart_deep:
                self.set_run_dir(self.run_dir,mode='create')
                self.update_config()
                self.write_config()
                self.copy_files_for_restart()
                                
                # If/when this gets smarter, say overriding BCs, it will have to become
                # more granular here. One option would be to create BC instances that know
                # how to copy over the original files and stanzas verbatim.
            else:
                # less sure about these.
                self.update_config()
                self.mdu.write()
                
    def copy_files_for_restart(self):
        """implied that this is a deep restart"""

        # The restart equivalent of these steps in write():
        #   self.write_extra_files()
        #   self.write_forcing()
        #   self.write_grid()
        
        # hard to know what all files we might want.
        # include any tim, pli, pliz, ext, xyz, ini
        # restart version of partition I think handles the grid?
        # also include any file that appears in FlowFM.ext
        # (because some forcing input like wind can have weird suffixes)
        # and include the original grid (check name in mdu)
        
        # skip any .steps, .cache
        # skip any mdu
        # probably skip anything without an extension
        with open(self.restart_from.mdu.filepath(('external forcing','ExtForceFile'))) as fp:
            flowfm_ext=fp.read()
        with open(self.mdu.filename) as fp:
            flowfm_mdu=fp.read()

        for fn in os.listdir(self.restart_from.run_dir):
            _,suffix = os.path.splitext(fn)
            do_copy = ( (suffix in ['.tim','.pli','.pliz','.ext','.xyz','.ini','.xyn'])
                        or (fn in flowfm_ext)
                        or (fn in flowfm_mdu)
                        or (fn==self.mdu['geometry','NetFile']) )
            # a bit kludgey. restart paths often include DFM_OUTPUT_flowfm, but definitely
            # don't want to copy that.
            fn_path=os.path.join(self.restart_from.run_dir,fn)
            if fn.startswith('DFM_OUTPUT') or os.path.isdir(fn_path):
                do_copy=False
                
            if do_copy:
                shutil.copyfile(fn_path, os.path.join(self.run_dir,fn))
            
                
            


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
    # model=old_model.create_restart(deep=False,mdu_suffix=args.suffix)
    model=old_model.create_restart(deep=True,run_dir=old_model.run_dir+args.suffix)
    assert not os.path.exists(model.run_dir)

    model.run_start=np.datetime64(args.start)

    duration=np.timedelta64(int(args.duration[:-1]), args.duration[-1])
    model.run_stop=model.run_start + duration
    
    # Alter settings as needed
    # For now assume we want roughly "full" output
    model.mdu['output','mapinterval'] = 30*60 # half hour
    model.mdu['output','Wrimap_velocity_vector'] = 1
    model.mdu['output','Wrimap_turbulence']=1

    model.write()
    model.partition()

    if not args.dryrun:
        try:
            model.run_simulation()
        except Exception as exc:
            log.error("run_simulation failed",exc_info=True)
    return model
 
if __name__=='__main__':
    main()

# testing:
# model=main(['--mdu',"data_2016_2d_asbuilt_impaired/flowfm.mdu",
#             '--start',"2016-08-04T00:00",
#             '--duration',"36h",
#             '--suffix','r000',
#             '--dryrun'])



