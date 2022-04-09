import local_config
import os
import numpy as np

class NMScenarioMixin(object):
    """
    Mixin that implements base configuration and alternative scenarios
    intercepts setting the grid and structures
    """
    terrain='asbuilt'
    scenario=''

    def set_grid_and_features(self):
        super().set_grid_and_features()

        # Is there a scenario-specific DEM overlay?
        if self.scenario=="":
            self.log.info("set_grid_and_features: Using base scenario.")
            return

        scen_overlay=os.path.join(local_config.bathy_dir,self.scenario,'output_res1.tif')
        if os.path.exists(scen_overlay):
            self.log.info("set_grid_and_features: Applying overlay %s"%scen_overlay)
            self.apply_dem_overlay(scen_overlay)
        else:
            self.log.info(f"Scenario {self.scenario} does not have a DEM overlay")

    def apply_dem_overlay(self,scen_overlay):
        """
        Update grid bathy and fixed weirs
        """
        # Import within function to avoid issues with libraries during BMI run.
        from stompy.spatial import field
        from stompy import utils
        import stompy.model.delft.io as dio
        
        dem=field.GdalGrid(scen_overlay)

        # Mimics ../grids/*/add_bathy_to_grid, but allowing for an ovelay dem
        # that doesn't cover the whole area
        if True: # gen_weirs
            self.log.info("Updating fixed weirs")
            for i in range(len(self.fixed_weirs)):
                # fixed_weirs[i] => (feature_label, N*M values, N labels)
                xyz__=self.fixed_weirs[i][1]
                assert xyz__.shape[1]==5 # should be x, y, and z and two heights that I ignore

                overlay=dem(xyz__[:,:2])
                z=np.where(np.isnan(overlay),
                           xyz__[:,2],
                           overlay)
                xyz__[:,2]=z

        if True: # gen_grids:
            g=self.grid
            self.log.info("Setting bathymetry overlay for scenario %s"%self.scenario)

            alpha=np.linspace(0,1,5)
            edge_z_min=np.full( g.Nedges(), np.nan, np.float64)

            # Find min depth of each edge:
            edge_select=self.grid.edge_clip_mask(dem.extents)

            self.log.info("Checking %d edges for new depth"%(edge_select.sum()))
            
            for j in utils.progress(np.nonzero(edge_select)[0]):
                pnts=(alpha[:,None] * g.nodes['x'][g.edges['nodes'][j,0]] +
                      (1-alpha[:,None]) * g.nodes['x'][g.edges['nodes'][j,1]])
                z=dem(pnts)
                if np.any(np.isnan(z)):
                    continue
                edge_z_min[j]=z.min()

            z_node=g.nodes['node_z_bed']
            updates=[]
            for n in utils.progress(range(g.Nnodes())):
                overlay=edge_z_min[g.node_to_edges(n)].min()
                if np.isfinite(overlay):
                    delta=overlay-z_node[n]
                    if np.abs(delta)<1e-3:
                        updates.append(np.nan)
                    else:
                        updates.append(delta)
                    z_node[n]=overlay
            self.log.info("Updated %d nodes, %d nonzero, mean change of %.2f"%(len(updates), np.isfinite(updates).sum(),
                                                                               np.nanmean(updates)))

    def add_pch_structure(self):
        if self.scenario=="":
            return super().add_pch_structure()
        elif self.scenario in ['scen1','scen2']:
            z_crest=2.1 # invert elevation
            height = 2*0.3048 # two feet
            area=2*np.pi * (0.5*0.3048)**2
            width=area/height
            z_levee=4.1
            gate_height=z_levee - (z_crest+height)
            assert gate_height>0,"Dimensions for PCH gate given negative gate height"
            
            self.add_Structure(
                type='gate',
                name='pch_gate',
                GateHeight=gate_height, # top of door to bottom of door
                GateLowerEdgeLevel=z_crest + height, # elevation of top of culvert
                GateOpeningWidth=0.0, # gate does not open
                CrestLevel=z_crest, 
                CrestWidth=width, # to conserve the same effective cross section
            )
        elif self.scenario=='scen3':
            self.add_Structure(
                type='weir',
                name='pch_gate',
                CrestLevel=2.75
            )
        else:
            raise Exception(f"Scenario {self.scenario} not implemented")
        
    def add_nmc_structure(self):
        if self.scenario=="":
            super().add_nmc_structure()
        elif self.scenario in ['scen1','scen2']:
            self.add_Structure(
                type='weir', 
                name='nmc_gate',
                CrestLevel=2.1 # MHHW+1ft
            )
        elif self.scenario=='scen3':
            pass # bathy update makes it irrelevant
        else:
            raise Exception(f"Scenario {self.scenario} not implemented")
        
    def add_nm_ditch_structure(self):
        if self.scenario=="":
            super().add_nm_ditch_structure()
        elif self.scenario in ['scen1','scen2','scen3']:
            self.add_Structure(
                type='weir', 
                name='nm_ditch_gate',
                CrestLevel=2.1 # MHHW+1ft
            )
        else:
            raise Exception(f"Scenario {self.scenario} not implemented")
    
    
