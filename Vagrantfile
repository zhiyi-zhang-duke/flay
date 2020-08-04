#BOX_IMAGE = "centos/7"
#BOX_VERSION = "1902.01"

Vagrant.configure("2") do |config|
    config.vm.box = "centos/7"
    config.vm.box_version = "1902.01"
    config.vm.provider "docker" do |subconfig|
        subconfig.build_dir = "./deployments/"

        subconfig.vm.network "flask_forwarded_port", guest: 5000, host: 5000
        subconfig.vm.synced_folder "./app", "/app", type: "nfs" 
    end
end
