# vcenter_logic.py

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

# Disable SSL certificate verification for the connection (if needed)
def connect_to_vcenter(vcenter_ip, username, password):
    """Connects to vCenter and returns a service instance."""
    try:
        # Bypass SSL certificate verification for testing environments (remove for production)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE

        # Connect to vCenter
        si = SmartConnect(host=vcenter_ip, user=username, pwd=password, sslContext=context)
        print(f"Successfully connected to {vcenter_ip}")
        return si
    except Exception as e:
        print(f"Could not connect to vCenter: {str(e)}")
        return None

def get_datacenters(content):
    """Retrieves a list of datacenters."""
    try:
        datacenters = [dc.name for dc in content.rootFolder.childEntity if isinstance(dc, vim.Datacenter)]
        return datacenters
    except Exception as e:
        print(f"Error retrieving datacenters: {str(e)}")
        return []

def get_folders(content, datacenter_name):
    """Retrieves folders in the specified datacenter."""
    try:
        datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)
        vm_folder = datacenter.vmFolder
        folders = [folder.name for folder in vm_folder.childEntity if isinstance(folder, vim.Folder)]
        return folders
    except Exception as e:
        print(f"Error retrieving folders: {str(e)}")
        return []

def get_clusters(content, datacenter_name):
    """Retrieves clusters in the specified datacenter."""
    try:
        datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)
        clusters = [cluster.name for cluster in datacenter.hostFolder.childEntity if isinstance(cluster, vim.ClusterComputeResource)]
        return clusters
    except Exception as e:
        print(f"Error retrieving clusters: {str(e)}")
        return []

def get_datastores(content, datacenter_name):
    """Retrieves datastores in the specified datacenter."""
    try:
        datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)
        datastores = [(ds.name, ds.summary.freeSpace) for ds in datacenter.datastore]
        return datastores
    except Exception as e:
        print(f"Error retrieving datastores: {str(e)}")
        return []

def create_server(content, server_name, datacenter_name, cluster_name, datastore_name, template_name, num_cpus, ram_mb, network_name):
    """Clones a VM from a template with specified configurations."""
    try:
        # Retrieve datacenter
        datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)

        # Retrieve cluster
        cluster = next(cluster for cluster in datacenter.hostFolder.childEntity if cluster.name == cluster_name)

        # Retrieve datastore
        datastore = next(ds for ds in datacenter.datastore if ds.name == datastore_name)

        # Template retrieval (assuming templates are in the datacenter)
        template = next(vm for vm in datacenter.vmFolder.childEntity if vm.name == template_name)

        # Clone VM from template
        vm_folder = datacenter.vmFolder

        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.pool = cluster.resourcePool

        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = False

        # Customization of the VM
        config = vim.vm.ConfigSpec()
        config.numCPUs = num_cpus
        config.memoryMB = ram_mb

        # Add network interface (assumes there is a network portgroup with the provided name)
        network = next(net for net in datacenter.network if net.name == network_name)
        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        nic_spec.device = vim.vm.device.VirtualVmxnet3()
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nic_spec.device.backing.network = network
        nic_spec.device.backing.deviceName = network_name

        config.deviceChange = [nic_spec]

        # Apply the configuration to the clone spec
        clonespec.config = config

        # Clone the VM
        print(f"Cloning {server_name} from template {template_name}...")
        task = template.Clone(folder=vm_folder, name=server_name, spec=clonespec)
        task_info = task.info

        # Check task status
        while task_info.state == vim.TaskInfo.State.running:
            task_info = task.info

        if task_info.state == vim.TaskInfo.State.success:
            print(f"Successfully cloned VM {server_name}")
        else:
            print(f"VM clone failed: {task_info.error.msg}")
    except Exception as e:
        print(f"Error creating server: {str(e)}")
