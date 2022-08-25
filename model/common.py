import numpy as np

section_signed_fields=['cross_section_discharge',
                       'cross_section_salt',
                       'cross_section_cumulative_discharge',
                       'cross_section_velocity',
                       'cross_section_cumulative_salt']
section_geom_fields=['cross_section_geom_node_coordx',
                       'cross_section_geom_node_coordy',
                       'cross_section_geom']
def prechain(dss):
    if len(dss)<2:
        return dss
    else:
        out=[dss[0]]
        # check for sections changing:
        # starting from the beginning
        secs0=dss[0].cross_section.values
        geoms0=dss[0].cross_section_geom
        for ds in dss[1:]:
            secs=ds.cross_section.values
            if np.all(secs[:len(secs0)]==secs0):
                if len(secs)>len(secs0):
                    sec_slice=slice(None,len(secs0))
                    secNode_slice=slice(None,dss[0].dims['cross_section_geom_nNodes'])
                    ds=ds.isel(cross_section=sec_slice,cross_section_geom_nNodes=secNode_slice)
                    print("Trimming out extra sections from later output")
            else:
                raise Exception("Section names don't match")
                
            # And check for n_complex_xs being flipped. For now, go with
            # the starting orientation:
            # prechain() is called *after* these become dask dataframes, which has a 
            # side effect of making the shapely geometries into arrays. 
            for sec in ['n_complex_xs']:
                geom0=geoms0.sel(cross_section=sec).values
                geomN=ds.cross_section_geom.sel(cross_section=sec).values
                if np.allclose(geom0,geomN):
                    print("Geometries match?")
                    continue
                elif np.allclose(geom0,geomN[::-1]):
                    # Probably have to construct a list of signed variables,
                    # flip each one...
                    flipper=np.where(secs0==sec,-1,1)
                    ds['flipper']=('cross_section',),flipper
                    for fld in section_signed_fields:  # e.g. 'cross_section_discharge'
                        print(f"Flipping variable {fld}")
                        ds[fld] = ds[fld] * ds['flipper']
                    del ds['flipper']
                    for fld in section_geom_fields:
                        ds[fld]=dss[0][fld]
            out.append(ds)
        return out
