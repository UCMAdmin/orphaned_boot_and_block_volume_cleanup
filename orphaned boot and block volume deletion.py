import oci
Regions = ["orasenatdecanational02_iad","orasenatdecanational02_phx","orasenatdecanational02_london"]
for reg in Regions:
        config = oci.config.from_file("~/.oci/orphaned_boot_block_config", profile_name=reg)
        IC=oci.identity.IdentityClient(config)
        compute=oci.core.ComputeClient(config)
        blockstorage=oci.core.BlockstorageClient(config)

        #Functions

        def clean_orphaned_boot_volumes(BootVols):
                x=BootVols
                for i in x:
                        blockstorage.delete_boot_volume(boot_volume_id=i)

        def clean_orphaned_block_volumes(BlockVols):
                x=BlockVols
                for i in x:
                        blockstorage.delete_volume(volume_id=i)

        #Fetching all the compartments id

        def get_compartment_ids(root_compartment_id):
                CL=oci.pagination.list_call_get_all_results(IC.list_compartments,root_compartment_id,compartment_id_in_subtree=True).data
                comp_ids=[i.id for i in CL if i.lifecycle_state=="ACTIVE"]
                # all_comp_ids=[i.id for i in CL]
                # print(len(comp_ids))
                # print(len(all_comp_ids))
                return comp_ids

        all_compartment_ids=get_compartment_ids("ocid1.tenancy.oc1..aaaaaaaapf32iocmevidwi4ujtrnfvq456dp4elubzvw564v6lh2sby24uua")

        for comp in all_compartment_ids:

                #Boot Volumes Part Starts

                DetachedBootVols = []
                BootVolAtt=compute.list_boot_attachments(compartment_id=comp).data
                for i in BootVolAtt:
                        if(i.lifecycle_state == "DETACHED"):
                                DetachedBootVols.append(i.boot_volume_id)

                #Boot Volumes Part Ends

                #Block Volumes Part Starts

                AttachedBlockVols = []
                AvailableBlockVols = []
                OrphanedBlockVols = []
                LBVA=compute.list_volume_attachments(compartment_id=comp).data

                for i in LBVA:
                        AttachedBlockVols.append(i.volume_id)


                LBV=blockstorage.list_volumes(compartment_id=comp).data
                for i in LBV:
                        AvailableBlockVols.append(i.id)


                for i in AvailableBlockVols:
                        if i not in AttachedBlockVols:
                                OrphanedBlockVols.append(i)

                #Block Volumes Part Ends



                #Functions Calling

                clean_orphaned_block_volumes(OrphanedBlockVols)

                clean_orphaned_boot_volumes(DetachedBootVols)
