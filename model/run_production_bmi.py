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
import sys, os, glob, time, logging, subprocess, shutil
import numpy as np
from stompy import utils
import xarray as xr
import local_config

os.environ['NUMEXPR_MAX_THREADS']='1'

class PescaBmiSeepageMixin(object):
    extraresistance=8.0

    evap=True

    def set_atmospheric_bcs(self):
        if self.evap:
            super().set_atmospheric_bcs()
        else:
            self.log.warning("Evaporation is disabled")
    
    def configure_global(self):
        super().configure_global()
        
        # For long run, pare down the output even more
        # restarts were 10G, should now be 4G
        self.mdu['output','RstInterval']=10*86400 # 345600
        # maps were 12G, should now be 3G
        self.mdu['output','MapInterval']=2*86400
        # history was 6G, and stays about the same.
        self.mdu['output','Wrihis_temperature']=0

        # DBG: maybe having a non-default value here is problematic?
        #self.log.warning("Leave Epshu to default value")
        #del self.mdu['numerics','Epshu'] # 5mm wet/dry threshold

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
            
    def add_pch_structure(self):
        z_crest=0.5 # The design plans for the culverts put base at -1ft NGVD --> 0.5m NABD88
        height = 1.2 # height of the culverts (48in)

        # Praying that a general structure avoided potential DFM bug, but it didn't.
        # But monkeying with a bunch of the parameters was sufficient.
        # Unclear on which ones avoided the instability (and whether a longer run will still
        # get the instability...)
        # {Up,Down}StreamWidth{1,2} = 10 => stable in v13, 20=>unstable in v11
        # {Up,Down}StreamLevel{1,2} = -0.5 => stable in v13, 0=>unstable in v11
        # GateHeight = 2.0 stable in v13, 1.5 => unstable in v11
        # extraresistance = 1.0 stable in v13, 0.0 => unstable in v11
        self.add_Structure(
            type='generalstructure',
            name='pch_gate',
            Upstream2Width=10,                 	# Width left side of structure (m)
            Upstream1Width=10,                 	# Width structure left side (m)
            CrestWidth=self.pch_area/height,   	# Width structure centre (m)
            Downstream1Width=10,                 	# Width structure right side (m)
            Downstream2Width=10,                 	# Width right side of structure (m)
            Upstream2Level=-0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=-0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=z_crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=-0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=-0.5,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=z_crest + height, # elevation of top of culvert
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
            extraresistance=1.0,                   	# Extra resistance (-)
            GateHeight=2.0, # top of door to bottom of door
            GateOpeningWidth=0.0, # gate does not open
        )

    def add_butano_weir_structure(self):
        # With SLR runs, ran into stability problems at Butano weir.
        # It looks a bit like the PCH instability, so will try the same fix.
        # on cws-linuxmodeling, seem to have some trouble with this structure
        # overtopping properly.  besides, the weir is very porous.
        # so make the top 1m have a 5cm gap.
        # Aside from accounting for some porosity, this appears to have made
        # the runs more stable. none of these runs had any issues (at least in 2D).
        self.add_Structure(
            type='generalstructure',
            name='butano_weir',
            Upstream2Width=10,                 	# Width left side of structure (m)
            Upstream1Width=10,                 	# Width structure left side (m)
            CrestWidth=8.0,   	# Width structure centre (m)
            Downstream1Width=10,                 	# Width structure right side (m)
            Downstream2Width=10,                 	# Width right side of structure (m)
            Upstream2Level=-0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=-0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=1.0,	# Bed level at centre of structure (m AD)
            Downstream1Level=-0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=-0.5,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=1.0, # elevation of top of culvert
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
            extraresistance=1.0,                   	# Extra resistance (-)
            GateHeight=1.0, # should be below crest, and ignored
            GateOpeningWidth=0.05, # gap to mimic porosity
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
        
        options += ['--mdu',self.mdu.filename]

        if num_procs>1:
            real_cmd = real_cmd + ["--mpi=%s"%self.mpi_flavor] + options
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

    # -n only used for driver_main, not --bmi
    parser.add_argument('-n','--num-cores',help='Number of cores',
                        default=local_config.LocalConfig.num_procs, type=int)

    parser.add_argument('-s','--scenario',help='Select scenario (scen1,scen2,scen2)',
                        default='')

    parser.add_argument('-f','--flow-regime',help='Select flow regime (impaired, unimpaired)',
                        default='impaired')
    
    parser.add_argument('-p','--period',help='Select run period (2013, 2016, 2016long)',
                        default='2016',type=str)

    parser.add_argument('-t','--three-d',help='Run in 3D',
                        action='store_true')

    parser.add_argument('--terrain',default='asbuilt',help='Select base terrain DEM')
    
    parser.add_argument('-r','--run-dir',help='override default run_dir',
                        default=None,type=str)

    parser.add_argument('-l','--layers',help='Number of z layers',default=50,type=int)

    # parser.add_argument('-c','--continue',help='continue from existing run')

    parser.add_argument('--debug-salt',help="Set all salt values to 32",action='store_true')

    parser.add_argument('--temperature',help="Enable temperature",action='store_true')

    parser.add_argument('--slr',help='Sea level rise offset in meters',default=0.0,type=float)

    # Get the MPI flavor to know how to identify rank and start the tasks
    parser.add_argument("-m", "--mpi", help="Enable MPI flavor",default=local_config.LocalConfig.mpi_flavor)

    args = parser.parse_args(argv)

    if args.bmi:
        assert args.mdu is not None
        task_main(args)
    else:
        driver_main(args)

def driver_main(args):
    import pesca_base # this is going to be problematic
    import nm_scenarios
    
    class PescaBmiSeepage(nm_scenarios.NMScenarioMixin,PescaBmiSeepageMixin,pesca_base.PescaButano):
        pass

    kwargs=dict(terrain=args.terrain,
                z_max=3.0,z_min=-0.5,
                extraresistance=8,
                scenario=args.scenario,
                num_procs=args.num_cores,
                nlayers_3d=args.layers,
                debug_salt=args.debug_salt,
                flow_regime=args.flow_regime)
        
    run_dir="data"

    if args.period=='2016':
        kwargs['run_start']=np.datetime64("2016-07-15 00:00")
        kwargs['run_stop']=np.datetime64("2016-12-16 00:00")
        run_dir += "_2016"
    elif args.period=='2016long':
        kwargs['run_start']=np.datetime64("2016-07-01 00:00")
        kwargs['run_stop']=np.datetime64("2017-02-28 00:00")
        run_dir += "_2016long"
    elif args.period=='2013':
        kwargs['run_start']=np.datetime64("2013-03-22 12:00")
        kwargs['run_stop']=np.datetime64("2014-03-08 00:00")
        run_dir += "_2013"
    elif "," in args.period:
        arg_start,arg_stop=args.period.split(',')
        kwargs['run_start']=np.datetime64(arg_start)
        kwargs['run_stop']=np.datetime64(arg_stop)
    else:
        raise Exception("Unknown period '%s'"%args.period)
    
    if args.three_d:
        kwargs['salinity']=True
        kwargs['temperature']=args.temperature # try to save some time
        run_dir+="_3d"
    else:
        kwargs['salinity']=False
        kwargs['temperature']=args.temperature
        run_dir+="_2d"

    run_dir+=f"_{kwargs['terrain']}"
    run_dir+=f"_{args.flow_regime}"

    if kwargs['scenario']!='':
        run_dir+=f"_{kwargs['scenario']}"

    if args.slr!=0.0:
        kwargs['slr']=args.slr
        run_dir+=f"_slr{args.slr:.2f}m"

    if args.run_dir is not None:
        run_dir=args.run_dir

    suffix=0
    for suffix in range(100):
        if suffix==0:
            test_dir=run_dir
        else:
            test_dir=run_dir+f"-v{suffix:03d}"
        if not os.path.exists(test_dir):
            kwargs['run_dir']=test_dir
            break
    else:
        raise Exception("Failed to find unique run dir (%s)"%test_dir)
    
    model=PescaBmiSeepage(**kwargs)
    
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
    # v00: ran okay, but accidentally ran as serial.
    # v01: crashes around 11.56d. Still diagnosing.
    # v02: try as 3D. 1 layer segfaulted. 3 layers is running.
    # v03: run as 3D with 1 layer, switch to sigma to maybe avoid segfault?
    #   no luck.
    # Back to 2D, after fixing some nans. 3D with 1 layer never worked.
    # v04: After fixing SLR and a logging problem, run a shorter, real 2D case.
    #      keep SLR=0.0 for better replication.
    # v05: Same, but trying 2022.02
    # Both of those appear to be suffering from the same issue -- end up stuck at dt=0.03
    # the good news is that they are almost done. Bad news is that they're super slow at this
    # point.
    # v06:  try these settings:
    # model.mdu['geometry','ChangeVelocityAtStructures']=1
    # model.mdu['time','AutoTimestepNoStruct']=1
    #   those allowed it to run, but it still had a weird oscillation at 6/10.
    # v07:  omit the ChangeVelocityAtStructures, since I haven't used that in the past.
    # v08:  just use ChangeVelocityAtStructures
    # v09: like v06, but with a general structure
    # v10: like v06, but with a weir and lots of output
    #      now it gets TWO of those transients, and the output window manages
    #      to fall exactly in between them.
    # v11: v09 structure, v10 output.
    #   - nothing weird in the tim forcing.
    #   - high-freq map output: some odd low spots in mesh2d_s1, notably on the
    #     east side of NM. But at map time step 60, start to see the perturbation.
    #     no real clues, though. fs goes up just upstream of the culverts, goes down
    #     just downstream of them. 
    # v11nobmi: copy that, bring in v06/seepage.tim, and run without bmi.
    #    does not look any different.
    # v12nobmi: similar, but also remove the pch structure entirely.
    #    avoids the large spikes, but still has some fluctuations in the NM that are suspect.
    #    maybe wind-driven setup? It's just a couple mm.
    #    the east side of NM continues to look odd. But I think it's just that the surface is
    #    overall higher, with a depression, and we happen to see it right as the depression
    #    starts to fill.
    # v13: change a bunch of structure settings. this seems to have stalled, but no idea why.
    #      seems like a dud node (c6-90)
    # v13r: just run it again. out of the gate running about 100x faster.
    #      that looks decent. no obvious weird signals.

    # Back to some long runs to see if everything is working.
    # v14: slr0ft, long run. CFLMax back to 0.7, hold breath
    #      slr2ft, long run.
    # model=PescaBmiSeepage(run_start=np.datetime64("2013-03-22 12:00"),
    #                       run_stop=np.datetime64("2014-03-08 00:00"),
    #                       # run_stop=np.datetime64("2013-06-15 00:00"), # DBG
    #                       run_dir="data_2013-2d-slr2ft-v14",
    #                       flow_regime='impaired',
    #                       scenario=args.scenario,
    #                       terrain='asbuilt',
    #                       slr=2*0.3048,
    #                       salinity=False, # set both to false to force 2D
    #                       temperature=False,
    #                       nlayers_3d=1, # 2D-ish
    #                       z_max=3.0,z_min=-0.5,
    #                       extraresistance=8)

    # still chasing things down...
    # model.mdu['geometry','ChangeVelocityAtStructures']=1
    model.mdu['time','AutoTimestepNoStruct']=1

    # 2022-04-06: any chance this helps?
    #  I think it helped a small amount, but may also have introduced
    #  salinity issues? New runs without this are painful, though with
    #  farm performance being unpredictable it's hard to sort out.
    # 2022-05-05: testing with short runs, nonzero value here was actually
    #  slower, and salinity no better. But in the early parts of the run
    #  it appears essential to include this, otherwise the first part of the
    #  the run is extremely slow.
    model.mdu['numerics','Drop3D']=-999
    # Try dropping this -- maybe that's what is causing these runs to be so slow.
    # model.mdu['numerics','Keepzlayeringatbed']=0
    # Praying that 0.5 is magic threshold.
    model.mdu['numerics','CFLMax'] = 0.40

    model.mdu['output','MbaInterval'] = 43200
    model.mdu['output','MbaWriteCSV'] = 1
    # model.mdu['time','Timestepanalysis'] = 1 # temporary

    model.write()

    shutil.copyfile(__file__,os.path.join(model.run_dir,os.path.basename(__file__)))
    shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
    shutil.copyfile("local_config.py",os.path.join(model.run_dir,"local_config.py"))
    with open(os.path.join(model.run_dir,"cmdlne"),'wt') as fp:
        fp.write(str(args))
        fp.write("\n")
        fp.write(" ".join(sys.argv))

    # Recent DFM has problems reading cached data -- leads to freeze.
    for f in glob.glob(os.path.join(model.run_dir,'*.cache')):
        os.unlink(f)
    if 'SLURM_JOB_ID' in os.environ:
        with open(os.path.join(model.run_dir,'job_id'),'wt') as fp:
            fp.write(f"{os.environ['SLURM_JOB_ID']}\n")

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
    if args.mpi is None:
        print("args.mpi is None")
        rank=0
    elif args.mpi in ['mpiexec','mpich','intel','slurm']:
        rank=int(os.environ['PMI_RANK'])
    else:
        raise Exception("Don't know how to find out rank")

    log_fn=os.path.join(os.path.dirname(args.mdu),f'log-{rank}')
    logging.basicConfig(filename=log_fn, level=logging.DEBUG)
    logging.debug("Top of task_main")
    logging.debug('This message should go to the log file')

    logging.debug(f"PID {os.getpid()}  rank {rank}")
    
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
            logging.debug(f"{k} => {os.environ[k]}")
            
    logging.info(f"[rank {rank}] about to open engine")

    sim=bmi.wrapper.BMIWrapper(engine=os.path.join(local_config.dfm_root,
                                                   "lib/libdflowfm.so"))
    logging.info(f"[rank {rank}] done with open engine")

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
    logging.info(f"[{rank}] about to initialize")
    sim.initialize(args.mdu)
    
    logging.info(f"[{rank}] initialized")

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
            logging.info("Will sleep to wait for hist_fn")
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
                logging.warning(f"rank {rank}  model time {t_now}  Failed to open history")
                logging.warning(str(exc))
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

                    L=100 # [m] closed state, across shore distance
                    W=100 # [m] along shore length of seepage outlet
                    k=0.012 # [m/s] hydraulic conductivity
                    z_bedrock=0.00 # [m]
                    if (h_src>z_bedrock):
                        Q=k * (h_src-z_bedrock)*L/W * (h_src-h_dst)
                    else:
                        Q=k * (1*0.001)/W           * (h_src-h_dst)
                    #Q*=1.65 # extra factor to get matching with QCM.
                    Q=max(0,Q*0.61) # 1.65 was from scatters. but looking at the time series coming out of
                    # the runs, this calculated flux was almost 3x too large. the 0.61 comes from scaling
                    # the previous output to best match the QCM fluxes (as output by the v04 model).
                    # Also go ahead and follow the one-directional flow that Dane suggested.
                    logging.info(f"[rank {rank}] t_model={t_now} h_src={h_src:.4f} h_dst={h_dst:.4f} Q={Q:.4f}")
                    # That is the last line I see in the log
                else:
                    Q=0.0

                t_new=(dt+t_now) / 60.0
                rec['fp'].write(f"{t_new+t_pad:.4f} {Q:.4f} {salt_temp}\n")
                rec['fp'].flush()

        t_bmi+=time.time() - t_last
        t_last=time.time()
        logging.info(f'taking a step dt={dt}')
        sim.update(dt)
        logging.info('Back from step')
        t_calc+=time.time() - t_last
        t_last=time.time()

        # Running via BMI will not fail out when the time step gets too short, but it will
        # return back to here without going as far as we requested.
        t_post=sim.get_current_time()
        if t_post<t_now+0.75*dt:
            logging.error("Looks like run has stalled out.")
            logging.error(f"Expected a step from {t_now} to {t_now+dt} but only got to {t_post}")
            logging.error("Will break out")
            break

        if rank==0:
            logging.info(f"t_bmi: {t_bmi}   t_calc: {t_calc}")
            
    sim.finalize()
    
if __name__=='__main__':
    main()
