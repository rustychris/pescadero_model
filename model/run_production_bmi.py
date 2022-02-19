# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:23:31 2021

@author: smunger, rustyh

Like run_production_final, but with BMI-based seepage for the mouth

Running this from head, after conda activate general and setting LD_LIBRARY_PATH, works.

srun --partition high2 --mpi=pmi2 --mem-per-cpu 4G -n 32 -N 1 --time 1:00:00 python ./test_bmi_load.py 

What about:
srun --partition high2 --mpi=pmi2 --mem-per-cpu 4G -n 32 -N 1 --time 1:00:00 python ./run_production_bmi.py --bmi --mpi=slurm --mdu=data_salt_filling-v05_existing_impaired/flowfm.mdu 
?

Seems that loading libdflowfm.so conflicts with some aspect of netCDF4 and ogr/osr.
Refactor such that BMI invocation imports very little.
"""
import sys
import os
import numpy as np
from stompy import utils
import xarray as xr
import subprocess, shutil
import time

os.environ['NUMEXPR_MAX_THREADS']='1'

class PescaBmiSeepageMixin(object):
    extraresistance=8.0

    def configure_global(self):
        super().configure_global()
        
        # For long run, pare down the output even more
        # restarts were 10G, should now be 4G
        self.mdu['output','RstInterval']=10*86400 # 345600
        # maps were 12G, should now be 3G
        self.mdu['output','MapInterval']=2*86400
        # history was 6G, and stays about the same.
        self.mdu['output','Wrihis_temperature']=0
    
    def add_mouth_structure(self):
        """
        Set up flow control structure for the inner and outer mouth structures
        """
        ds = self.prep_qcm_data()
        crest= ds['z_thalweg']
        width= ds['w_inlet']    

        for name in ['mouth','mouth_B']:
            self.add_Structure(
                type='generalstructure',
                name=name,
            
                Upstream2Width=100,                 	# Width left side of structure (m)
                Upstream1Width=100,                 	# Width structure left side (m)
                CrestWidth=100,                 	# Width structure centre (m)
                Downstream1Width=100,                 	# Width structure right side (m)
                Downstream2Width=100,                 	# Width right side of structure (m)
                Upstream2Level=0,                   	# Bed level left side of structure (m AD)
                Upstream1Level=0,                   	# Bed level left side structure (m AD)
                CrestLevel=crest,	# Bed level at centre of structure (m AD)
                Downstream1Level=0,                   	# Bed level right side structure (m AD)
                Downstream2Level=0,                   	# Bed level right side of structure (m AD)
                GateLowerEdgeLevel=0,                  	# Gate lower edge level (m AD)
                pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
                pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
                pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
                pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
                pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
                neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
                neg_drowngateflowcoeff=1,                  	# Negative drowned gate flow (-)
                neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
                neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
                neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
                extraresistance=self.extraresistance,                   	# Extra resistance (-)
                GateHeight=10,                   	# Vertical gate door height (m)
                GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
                )
        
    # BMI risky business
    seepages=['seepage']
    
    def write_monitors(self):
        # Include a monitor point for each end of any seepage
        # src_sinks
        for bc in self.bcs:
            for seepage in self.seepages:
                if bc.name==seepage:
                    self.add_monitor_points([ dict(name=seepage+'A',
                                                   geom=bc.geom.interpolate(0,normalized=True)),
                                              dict(name=seepage+'B',
                                                   geom=bc.geom.interpolate(1,normalized=True))])
        super().write_monitors()
    
    def run_simulation(self,threads=1,extra_args=[]):
        """
        BMI version, start simulation. 
        Ignores threads, extra_args
        """
        num_procs=self.num_procs

        # May need to get smarter if there is further subclassing
        real_cmd=['python',__file__,'--bmi']
        options=[]
        # Not sure I still need to pass in the seepages
        # for seepage in self.seepages:
        #     options+=["-s",seepage]
        options += ['--mdu',self.mdu.filename]

        if num_procs>1:
            #real_cmd = real_cmd + ["--mpi=intel"] + options
            real_cmd = real_cmd + ["--mpi=slurm"] + options
            return self.mpirun(real_cmd)
        else:
            real_cmd= real_cmd + options
            self.log.info("Running command: %s"%(" ".join(real_cmd)))
            subprocess.call(real_cmd)
    

        

## This set up for tidal conditions July 2016 (16 days), use extraresistance=8
# model=PescaChgMouth(run_start=np.datetime64("2016-07-09 00:00"),
#                               run_stop=np.datetime64("2016-07-25 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p07",
#                               salinity=False,
#                               temperature=False,
#                               extraresistance=8)

# # This set up for tidal condition July 2017 (31 days), use extraresistance=8
# model=PescaChgMouth(run_start=np.datetime64("2017-07-15 00:00"),
#                     run_stop=np.datetime64("2017-08-15 00:00"),
#                     run_dir="run_tide_test-p08",
#                     salinity=False,
#                     temperature=False,
#                     extraresistance=8)


# # This set up for breaching condition December 2016 (19 days), use extraresistance=1
# model=PescaChgMouth(run_start=np.datetime64("2016-12-10 00:00"),
#                               run_stop=np.datetime64("2016-12-29 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p06",
#                               salinity=False,
#                               temperature=False,
#                               extraresistance=1)

def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description='Run Pescadero hydro model.')
    parser.add_argument('-b','--bmi',action='store_true',
                        help='run as a BMI task')
    parser.add_argument('--mdu',help='Path to MDU file when run as BMI task')
    # Get the MPI flavor just to know how to identify rank
    parser.add_argument("-m", "--mpi", help="Enable MPI flavor",default=None)

    args = parser.parse_args(argv)

    if args.bmi:
        assert args.mdu is not None
        task_main(args)
    else:
        driver_main(args)

def driver_main(args):
    import pesca_base # this is going to be problematic
    import local_config
    
    class PescaBmiSeepage(PescaBmiSeepageMixin,pesca_base.PescaButano):
        pass

    # model=PescaBmiSeepage(run_start=np.datetime64("2016-07-15 00:00"),
    #                       run_stop=np.datetime64("2016-12-16 00:00"),
    #                       run_dir="data_salt_filling-v05_existing_impaired",
    #                       flow_regime='impaired',
    #                       terrain='existing',
    #                       salinity=True,
    #                       temperature=True,
    #                       nlayers_3d=100,
    #                       z_max=3.0,z_min=-0.5,
    #                       extraresistance=8)

    # First go at 2013, very long, will start in 2D. Wind was probably not working for this.
    # model=PescaBmiSeepage(run_start=np.datetime64("2013-03-22 12:00"),
    #                       run_stop=np.datetime64("2014-03-08 00:00"),
    #                       run_dir="data_2013-2d-v00",
    #                       flow_regime='impaired', 
    #                       terrain='existing', # real runs will use asbuilt
    #                       salinity=False, # these false forces 2D
    #                       temperature=False,
    #                       nlayers_3d=1, # not really used
    #                       # z_max=3.0,z_min=-0.5,
    #                       extraresistance=8)

    # First go at SLR, very long, will start in 2D. 
    model=PescaBmiSeepage(run_start=np.datetime64("2013-03-22 12:00"),
                          run_stop=np.datetime64("2014-03-08 00:00"),
                          run_dir="data_2013-2d-slr2ft-v00",
                          flow_regime='impaired',
                          terrain='asbuilt',
                          slr=2*0.3048,
                          salinity=False, # these false forces 2D
                          temperature=False,
                          nlayers_3d=1, # not really used
                          # z_max=3.0,z_min=-0.5,
                          extraresistance=8)

    model.write()

    shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
    shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))

    model.partition()

    try:
        print(model.run_dir)
        if model.num_procs<=1:
            nthreads=8
        else:
            nthreads=1
        model.run_simulation(threads=nthreads)
    except subprocess.CalledProcessError as exc:
        print(exc.output.decode())
        raise


def task_main(args):
    print("Top of task_main")
    print("LD_LIBRARY_PATH")
    print(os.environ['LD_LIBRARY_PATH'])

    import local_config
    import bmi.wrapper
    from numpy.ctypeslib import ndpointer  # nd arrays
    from ctypes import (
        # Types
        c_double, c_int, c_char_p, c_bool, c_char, c_float, c_void_p,
        # Complex types
        # ARRAY, Structure,
        # Making strings
        # Pointering
        POINTER, byref, # CFUNCTYPE,
        # Loading
        # cdll
    )

    for k in os.environ:
        if ('SLURM' in k) or ('MPI' in k):
            print(f"{k} => {os.environ[k]}")
            
    if args.mpi is None:
        print("args.mpi is None")
        rank=0
    elif args.mpi in ['intel','slurm']:
        rank=int(os.environ['PMI_RANK'])
    #elif args.mpi=='slurm':
    #    rank=int(os.environ['SLURM_PROCID'])
    else:
        raise Exception("Don't know how to find out rank")

    print(f"[rank {rank}] about to open engine")
    sim=bmi.wrapper.BMIWrapper(engine=os.path.join(local_config.dfm_root,
                                                   "lib/libdflowfm.so"))
    print(f"[rank {rank}] done with open engine")

    # Just need to keep ahead of the model a little bit.
    dt=900.0 # update interval of the history file.

    # really just to get the list of seepages and the functions to handle them.
    model=PescaBmiSeepageMixin()
    model.run_dir=os.path.dirname(args.mdu)

    # Need to check the MDU to know if temp/salinity included
    import stompy.model.delft.io as dio
    mdu=dio.MDUFile(args.mdu)
    salt_temp=""
    if int(mdu['physics','salinity'])>0:
        salt_temp+=" 0.0"
    if int(mdu['physics','temperature'])>0:
        salt_temp+=" 0.0"
    # runs don't always start at the reference time
    tstart_min=float(mdu['time','tstart'])/60

    dt_min=mdu['numerics','MinTimestepBreak']
    if dt_min:
        dt_min=float(dt_min)
    
    if rank==0:
        seepages=[ dict(name=s) for s in model.seepages]

        for rec in seepages:
            t_pad=dt/60. # In minutes
            tim_fn=os.path.join(model.run_dir,f'{rec["name"]}.tim')
            rec['fp']=open(tim_fn,'wt')
            for t in [0.0,t_pad]: # HERE: may have to adjust for reference time
                rec['fp'].write(f"{t+tstart_min:.4f} 0.05{salt_temp}\n")
            rec['fp'].flush()

    # dfm will figure out the per-rank file
    # initialize changes working directory to where mdu is.
    print(f"[{rank}] about to initialize")
    sim.initialize(args.mdu)

    if rank==0:
        if args.mpi is None:
            hist_fn="DFM_OUTPUT_flowfm/flowfm_his.nc"
        else:
            hist_fn="DFM_OUTPUT_flowfm/flowfm_0000_his.nc"
        # hoping I can figure out where to pull stage here, instead of
        # in the time loop
        for waiting in range(10):
            if os.path.exists(hist_fn):
                break
            print("Will sleep to wait for hist_fn")
            sys.stdout.flush()
            time.sleep(2.0)
        else:
            raise Exception(f"history file {hist_fn} never showed up?!")
        ds=xr.open_dataset(hist_fn)
        
        stations=[s.decode().strip() for s in ds.station_name.values]
        ds.close()
        
        for rec in seepages:
            # index of this source_sink in the history output
            # ss_idx=[s.decode().strip()
            #         for s in ds['source_sink_name'].values].index(rec['name'])
            # x=ds.source_sink_x_coordinate.isel(source_sink=ss_idx).values
            # y=ds.source_sink_y_coordinate.isel(source_sink=ss_idx).values
            # rec['xy']=np.c_[x,y] # endpoints of the source_sink
            rec['src_mon_idx']=stations.index(rec['name']+'A')
            rec['snk_mon_idx']=stations.index(rec['name']+'B')
        
    # TASK TIME LOOP
    t_calc=0.0
    t_bmi=0.0
    t_last=time.time()
    while sim.get_current_time()<sim.get_end_time():
        t_now=sim.get_current_time()
        
        if rank==0:
            try:
                # try to streamline this, since we'll be doing it a lot and
                # CF decoding could get slow when the history file is large.
                ds=xr.open_dataset(hist_fn,decode_cf=False,decode_times=False,
                                   decode_coords=False)
            except Exception as exc:
                print(f"rank {rank}  model time {t_now}  Failed to open history")
                print(exc)
                ds=None

            for rec in seepages:
                if ds is not None:
                    t_hist=ds.time.values[-1]
                    # Excellent -- history output can be from this same time, so
                    # there isn't even a lag here.
                    # What all do I get in history? everything I need!
                    h_src=ds.waterlevel.isel(time=-1,stations=rec['src_mon_idx']).values
                    h_dst=ds.waterlevel.isel(time=-1,stations=rec['snk_mon_idx']).values

                    ds.close() # avoid xarray caching

                    # These values are loosely based on values from Dane Behrens,
                    # but liberally adjusted to get a seepage flux matching what 
                    # is output from the QCM during closed conditions. During open
                    # conditions the QCM predicts a larger flux, but for our purposes
                    # I don't think that matters too much.
                    L=200
                    W=50
                    k=0.0207 # m/s
                    z_bedrock=-1.37 # m NAVD88
                    Q=k*W/(2*L)*((h_src-z_bedrock)**2 - (h_dst-z_bedrock)**2)
                    print(f"[rank {rank}] t_model={t_now} h_src={h_src:.4f} h_dst={h_dst:.4f} Q={Q:.4f}")

                else:
                    Q=0.0

                t_new=(dt+t_now) / 60.0
                rec['fp'].write(f"{t_new+t_pad:.4f} {Q:.4f} {salt_temp}\n")
                rec['fp'].flush()

        t_bmi+=time.time() - t_last
        t_last=time.time()
        sim.update(dt)
        t_calc+=time.time() - t_last
        t_last=time.time()

        # Running via BMI will not fail out when the time step gets too short, but it will
        # return back to here without going as far as we requested.
        t_post=sim.get_current_time()
        if t_post<t_now+0.75*dt:
            print("Looks like run has stalled out.")
            print(f"Expected a step from {t_now} to {t_now+dt} but only got to {t_post}")
            print("Will break out")
            break

        if rank==0:
            print("t_bmi: ",t_bmi,"   t_calc: ",t_calc)
            sys.stdout.flush()
            
    sim.finalize()
    
if __name__=='__main__':
    main()
