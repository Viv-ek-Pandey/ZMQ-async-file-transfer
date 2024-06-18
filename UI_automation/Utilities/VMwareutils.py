from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from Constants.Constants import Constants
from Utilities.XLUtils import addTestResultToReportSheet
from Utilities.utils import getServiceInstance, waitForTask


def vmwareInfraCreation(data, filepath, logger):
   
    def createVirtualMachine(si, template_name, name, datacenter_name, cluster_name, datastore_name, num_vms):
        content = si.RetrieveContent()
        
        # Get Datacenter object
        datacenter = None
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter_name:
                datacenter = dc
                break
        
        if not datacenter:
            logger.error(Constants.DATACENTER_NOT_FOUND)
            return Constants.FAILED

        # Get Cluster object
        compute = None
        for cl in datacenter.hostFolder.childEntity:
            if isinstance(cl, vim.ClusterComputeResource) or isinstance(cl, vim.ComputeResource) and cl.name == cluster_name:
                compute = cl
                break
        
        if not compute:
            logger.error(Constants.COMPUTE_NOT_FOUND)
            return Constants.FAILED
        

        # Get Datastore object
        datastore = None
        for ds in datacenter.datastoreFolder.childEntity:
            if ds.name == datastore_name:
                datastore = ds
                break
        
        if not datastore:
            logger.error(Constants.DATASTORE_NOT_FOUND)
            return Constants.FAILED

        # Get VM template object
        template = None
        for vm in datacenter.vmFolder.childEntity:
            if vm.name == template_name:
                template = vm
                break

        if not template:
            logger.error(Constants.TEMPLATE_NOT_FOUND)
            return Constants.FAILED
        
        # Clone VMs
        for i in range(num_vms):
            vm_clone_name = f"{name}_{i+1}"
            clone_spec = vim.vm.CloneSpec()
            relocate_spec = vim.vm.RelocateSpec()
            relocate_spec.datastore = datastore
            relocate_spec.pool = compute.resourcePool
            clone_spec.location = relocate_spec
            clone_spec.powerOn = True
    
            task = template.Clone(folder=template.parent, name=vm_clone_name, spec=clone_spec)
            waitForTask(task)
            logger.info(Constants.VMWARE_CREATED_SUCCESSFULLY.format(vm_clone_name))
            addTestResultToReportSheet(filepath, Constants.INFRA_TEST, Constants.INFRA_HEADER, data, 
                                                Constants.VMWARE_CREATED_SUCCESSFULLY.format(vm_clone_name))
            

    def main():
        vcenter_host = data["vCenterServer"]
        vcenter_user = data["userName"]
        vcenter_pwd = data["password"]
        template_name = data["templateName"]
        name = data["name"]
        datacenter_name = data["dataCenterName"]
        cluster_name = data["clusterName"]
        datastore_name = "datastore1"
        num_vms = data["numberOfVirtualMachines"]

        si = getServiceInstance(vcenter_host, vcenter_user, vcenter_pwd)
        createVirtualMachine(si, template_name, name, datacenter_name, cluster_name, datastore_name, num_vms)

    main()
    return Constants.PASSED

def vmwareInfraDelete(data, filepath, logger):
    
    def get_obj(content, vimtype, name):
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        container.Destroy()
        return obj

    def delete_vm(si, name):
        content = si.RetrieveContent()
        vm = get_obj(content, [vim.VirtualMachine], name)
        if vm:
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                task = vm.PowerOffVM_Task()
                waitForTask(task)
            
            task = vm.Destroy_Task()
            waitForTask(task)
            logger.info(Constants.VMWARE_VM_DELETED_SUCCESSFULLY.format(name))

            addTestResultToReportSheet(filepath, Constants.INFRA_TEST, Constants.INFRA_HEADER, data, 
                                                Constants.VMWARE_VM_DELETED_SUCCESSFULLY.format(name))

        else:
            logger.info(Constants.VIRTUAL_MACHINE_NOT_FOUND.format(name))
            return Constants.FAILED
          

    def main():
        vcenter_host = data["vCenterServer"]
        vcenter_user = data["userName"]
        vcenter_pwd = data["password"]
        names = data["name"]

        si = getServiceInstance(vcenter_host, vcenter_user, vcenter_pwd)
        for name in names:
            delete_vm(si, name)

    main()
    return Constants.PASSED
