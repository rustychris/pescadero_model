"""
Based on run_restart_highres.py
But additionally sets up a dye tracer for NM and NP water.
"""

import stompy.model.delft.dflow_model as dfm
import os, shutil
import xarray as xr
import numpy as np
import logging

import local_config
class PescaBreachRestart(local_config.LocalConfig,dfm.DFlowModel):
    tracers=['marsh','pond'] # should match 'desc' of polygons with
    # type=='dye'
    
    # Have to be a bit manual about this because this isn't subclass
    # of the regular pesca base classes (b/c the restart logic hasn't
    # been worked out, specifically avoiding recreating the whole model
    # config)
    tracer_shp="../grids/pesca_butano_v08/polygon_features.shp"
    
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
                self.update_for_dye_release()
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

    def update_for_dye_release(self):
        """
        Update/copy restart files to reflect tracer IC.
        sequence: this will update self.mdu, so needs to be done
        prior, or needs to rewrite mdu
        """
        for tracer in self.tracers:
            pli_fn=f'ocean_bc_{tracer}.pli'

            with open(self.mdu.filepath(('external forcing','ExtForceFile')),'a') as fp:
                # since it's a restart, maybe it's safer to specify the tracer as a
                # BC.
                lines=[#"QUANTITY=initialbndtracer",
                    f"QUANTITY=tracerbnd{tracer}",
                    f"FILENAME={pli_fn}",
                    "FILETYPE=9",
                    "METHOD=3",
                    "OPERAND=O",
                    ""
                ]
                fp.write("\n".join(lines))
                # not super clean...
                shutil.copyfile(os.path.join(self.run_dir,'ocean_bc.pli'),
                                os.path.join(self.run_dir,f'ocean_bc_{tracer}.pli'))
                with open(os.path.join(self.run_dir,f'ocean_bc_{tracer}_0001.tim'),'wt') as fp:
                    fp.write("-1000000 0\n")
                    fp.write("0 0\n")
                    fp.write("5000000 0\n")

                # Source sinks need an extra column for the tracer
                for src_sink in ['seepage.tim','wave_overtop.tim']:
                    fn=os.path.join(self.run_dir,src_sink)
                    fnbak=os.path.join(self.run_dir,src_sink+'.bak')
                    shutil.move(fn,fnbak)
                    with open(fn,'wt') as fpout, open(fnbak,'rt') as fpin:
                        for line in fpin:
                            fpout.write(line.strip()+" 0.0\n")
        
        # And update the restart files -- which modifies the mdu...
        self.modify_restart_data(self.modify_restart_for_tracer)
        # so write the mdu again
        self.mdu.write()

    def modify_restart_for_tracer(self,ds,**kw):
        """
        Takes a dataset
        kw: 'proc', maybe others..
        """
        import shapely
        from stompy.spatial import wkb2shp
        poly_shp=os.path.join(os.path.dirname(__file__),
                              self.tracer_shp)
        polys=wkb2shp.shp2geom(poly_shp)

        # centroids
        xy=np.c_[ ds['FlowElem_xzw'].values,
                  ds['FlowElem_yzw'].values ]

        for tracer in self.tracers:
            hits= (polys['type']=='dye') & (polys['desc']==tracer)
            assert hits.sum()==1,f"Expected exactly one match for type=dye, desc={tracer} in {poly_shp}"
            geom=polys['geom'][hits][0]
            
            # add tracer field -- just make it look like salinity
            # should be something like (time,nFlowElem,laydim)
            tracer_val=np.zeros_like(ds['sa1'].values)
            for i,p in enumerate(xy):
                pnt=shapely.geometry.Point(p)
                if geom.contains(pnt):
                    tracer_val[0,i,...] = 1.0
            ds[tracer]=ds['sa1'].dims,tracer_val
        
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

    old_model=PescaBreachRestart.load(args.mdu)
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



