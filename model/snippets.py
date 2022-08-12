# Code related to finding a lagoon cell mask

# Do the volume check
t_high=np.datetime64('2016-07-31 04:30:00')
t_low =np.datetime64('2016-07-31 15:45:00')


def lagoon_cells(mds,his):
    # Select cells within the footprint of the lagoon
    # one cut at the mouth, one cut across Butano,Pesca,nm_complex, and the levee.
    butano_ls=his.cross_section_geom.sel(cross_section='butano_wide').item()
    pesca_ls =his.cross_section_geom.sel(cross_section='pesca_wide').item()
    nmarsh_ls=his.cross_section_geom.sel(cross_section='n_complex_xs').item()
    mouth_ls =his.cross_section_geom.sel(cross_section='mouth_xs').item()
    butano_xy=np.array(butano_ls.coords)
    pesca_xy=np.array(pesca_ls.coords)
    nmarsh_xy=np.array(nmarsh_ls.coords)

    from stompy.spatial import join_features

    joined=join_features.merge_lines(segments=[butano_xy,pesca_xy,nmarsh_xy])
    assert len(joined)==1
    joined=joined[0]

    levee_wkt="""LineString (552580.7926844070898369 4124429.30493242293596268, 552574.36160051822662354 4124431.44862705282866955, 552571.86791492870543152 4124434.64229456195607781, 552564.37437067192513496 4124438.46308161038905382, 552555.9097663820721209 4124441.6558709479868412, 552547.89066758123226464 4124444.10615113703534007, 552541.80209256568923593 4124445.4426676039583981, 552534.30275016860105097 4124448.48695511138066649, 552526.50640411220956594 4124450.19472615234553814, 552519.67531994846649468 4124453.31326457485556602, 552512.10172663652338088 4124455.24378836061805487, 552507.64667174709029496 4124457.17431214591488242, 552498.29105647990945727 4124459.62459233403205872, 552487.15341925644315779 4124463.18863624520599842, 552482.25285887811332941 4124465.56466551963239908, 552478.39181130728684366 4124467.34668747521936893, 552474.97626922547351569 4124470.019720409065485, 552470.96671982493717223 4124473.28676066128537059, 552472.00623263255693018 4124477.2963100615888834, 552470.96671982493717223 4124481.3058594623580575, 552467.40267591353040189 4124485.61241252208128572, 552462.94762102409731597 4124490.36447107046842575, 552454.33451490453444421 4124503.28413025010377169, 552448.83994720759801567 4124510.26371624320745468, 552441.56335755495820194 4124520.06483699986711144, 552438.14781547314487398 4124524.81689554871991277, 552434.13826607260853052 4124528.82644494902342558, 552426.11916727176867425 4124536.99404557980597019, 552417.50606115232221782 4124546.49816267704591155, 552408.00194405496586114 4124555.7052761148661375, 552394.48827755684033036 4124571.44647005712613463, 552385.13266228919383138 4124583.62362008821219206, 552377.85607263655401766 4124592.23672620765864849, 552372.80701042851433158 4124599.51331586064770818, 552367.60944639088120311 4124606.34440002404153347, 552355.13529270060826093 4124623.42211043369024992, 552347.26469572936184704 4124636.63877327088266611, 552340.87911705463193357 4124654.7559964875690639, 552338.80009143950883299 4124661.7355824806727469)"""
    from shapely import wkt, geometry
    levee=wkt.loads(levee_wkt)
    levee_xy=np.array(levee.coords)
    levee_xy # starts 552580.79268441, 4124429.30493242],
    joined # starts in almost the same place.
    cut=np.concatenate( [joined[::-1,:], levee_xy[1:,:]],axis=0)

    grid=mds.grid
    cut_geom=geometry.LineString(cut)
    lagoon_and_ocean = grid.select_cells_by_cut(cut_geom)

    ocean=grid.select_cells_by_cut(mouth_ls,side='right')

    lagoon=lagoon_and_ocean & ~ocean
    return lagoon



#------------

ti_high,ti_low=np.searchsorted(mds.time.values,[t_high,t_low])

volumes=[]
vol_times=[]
Acell=grid.cells_area()

for ti in range(ti_high,ti_low+1):
    vol_times.append(mds.time.values[ti])
    depth=mds['mesh2d_waterdepth'].isel(time=ti)
    V=np.sum(depth.values[lagoon]*Acell[lagoon])
    volumes.append(V)

# from cross section discharge
ti_high,ti_low=np.searchsorted(his.time.values,[t_high,t_low])
ti_slice=slice(ti_high,ti_low+1)
Q_times=his.time.isel(time=ti_slice).values
# Be sure to make a copy
Q_vols=np.zeros(len(Q_times),np.float64)
Q_vols-=his.cross_section_cumulative_discharge.sel(cross_section='mouth_xs').isel(time=ti_slice).values
Q_vols+=his.cross_section_cumulative_discharge.sel(cross_section='butano_wide').isel(time=ti_slice).values
Q_vols+=his.cross_section_cumulative_discharge.sel(cross_section='pesca_wide').isel(time=ti_slice).values
Q_vols+=his.cross_section_cumulative_discharge.sel(cross_section='n_complex_xs').isel(time=ti_slice).values


