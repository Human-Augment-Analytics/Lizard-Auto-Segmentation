import numpy as np
import nrrd as pynrrd
import open3d as o3d
import copy


def preprocess_point_cloud(pcd, voxel_size):
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def volume_to_point_cloud(volume, threshold=38000):
    temp = np.asarray((volume > threshold))
    z, y, x = temp.nonzero()
    points = np.vstack((x, y, z)).T  # Transpose to get points in (N, 3) format
    return points

def prepare_dataset(voxel_size, source_file=None, target_file=None):
    source_data, _ = pynrrd.read(source_file)
    target_data, _ = pynrrd.read(target_file)


    source_points = volume_to_point_cloud(source_data)
    target_points = volume_to_point_cloud(target_data)

    # Create Open3D point clouds
    source_pcd = o3d.geometry.PointCloud()
    target_pcd = o3d.geometry.PointCloud()


    source_pcd.points = o3d.utility.Vector3dVector(source_points)
    target_pcd.points = o3d.utility.Vector3dVector(target_points)

    source_down, source_fpfh = preprocess_point_cloud(source_pcd, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target_pcd, voxel_size)
    return source_data, target_data, source_down, target_down, source_fpfh, target_fpfh

def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.95),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(20000, 1000))
    return result

def process(max_iters=5):
    iternum = 0
    reg_icp = None
    result_ransac = None
    stop = False
    while(not stop):
        #do preprocess (downsampled)
        voxel_size = 15
        source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(
                        voxel_size, source_file, target_file)
        #do global registration
        result_ransac = execute_global_registration(source_down, target_down,
                                                source_fpfh, target_fpfh,
                                                voxel_size)
        st = source_down.transform(result_ransac.transformation)
        #draw_registration_result(st, target_down, np.eye(4))
        print(result_ransac.fitness, result_ransac.inlier_rmse)
        #do crop
        bbox = st.get_minimal_oriented_bounding_box()
        bbox.extent = bbox.extent * 2
        tt = target_down.crop(bbox)
        #o3d.visualization.draw_geometries([st, bbox, tt])
        #do preprocess
        source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(
                        3, source_file, target_file)
        st = source_down.transform(result_ransac.transformation)
        tt = target_down.crop(bbox)
        #do local registration
        threshold=1000
        trans_init = np.eye(4)  # initial transformation
        reg_icp = o3d.pipelines.registration.registration_icp(
                        st, tt, threshold, np.eye(4),
                        o3d.pipelines.registration.TransformationEstimationPointToPoint(with_scaling=True),
                        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=1000, relative_fitness=.000000000000001, relative_rmse=.0000000000001)
                        )
        print(reg_icp.inlier_rmse)
        st = st.transform(reg_icp.transformation)
        #draw_registration_result(st, target_down, np.eye(4))
        #do crop
        bbox2 = st.get_minimal_oriented_bounding_box()
        bbox2.extent = bbox2.extent * 1.15
        tt = tt.crop(bbox2)
        #o3d.visualization.draw_geometries([st, bbox2, tt])
        if(reg_icp.inlier_rmse < 6):    #if rmse of ICP registration <5, good fit achieved
            stop = True
            print('Sample met stopping condition for minimizing error')
            #draw_registration_result(st, tt, np.eye(4))
        if(iternum >= max_iters):       #if maximum number of retries occurs with no good fit, notfiy user to process manually
            stop = True
            print('Reached max iterations, alignment of this sample should be adjusted manually')
        iternum = iternum + 1
    return result_ransac, reg_icp