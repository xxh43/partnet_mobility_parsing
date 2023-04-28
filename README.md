# partnet_mobility_parsing

‘geo/shape_id/result.json’  file contains the mesh tree structure , each node may or may not have a list of children nodes, each leaf node contains the mesh file id. 

‘precomputed/shape_id.json’ file contains the information specifying which subparts make up a high level part. 

These above 2 files combined you can know the high level part (the part that corresponds to a motion) decomposition of each shape. And the ‘precomputed/shape_id.json’  file also contains the connectivity graph of the high level part.  

I think ‘geo/shape_id/result_after_merging.json’ might be the combined version of the above 2 files (not sure)

Then the ‘geo/shape_id/textured_objs’ folder contains the mesh data in obj format.

Finally  the ‘geo/shape_id/mobility_v2.json’ file contains the groundtruth motion data for each high level part id
