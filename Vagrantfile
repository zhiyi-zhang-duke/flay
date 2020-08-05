#BOX_IMAGE = "centos/7"
#BOX_VERSION = "1902.01"

$web_script = <<-SCRIPT
apt-get update && apt-get upgrade -y
apt-get install python-pip apache2 apache2-dev -y
pip install flask pymongo
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.6.5.tar.gz 4.6.5.tar.gz
tar -xf 4.6.5.tar.gz \
    && cd mod_wsgi-4.6.5 \
	&& ./configure \
	&& make install
rm -rf /mod_wsgi-4.6.5
rm 4.6.5.tar.gz
apt-get autoremove -y
SCRIPT

$db_script = <<-SCRIPT
apt-get update && apt-get upgrade -y
apt-get install python-pip apache2 apache2-dev -y
sudo apt-get install mongodb -y
apt-get autoremove -y
SCRIPT

NODES_COUNT = 1
RAM_MB = 1024
CORE_COUNT = 2
#BOX = "centos/7"


Vagrant.configure("2") do |config|

  (1..NODES_COUNT).each do |i|
    config.vm.define "web#{i}", primary: true do |server|
      server.vm.box = "generic/ubuntu1604"
      #Weird syntax is just naming multiple boxes (box#1, box#2, etc.)
      server.vm.hostname = "box#{i}"

      server.vm.provider "virtualbox" do |v|
      	#Weird syntax is just naming multiple providers (web#1, web#2, etc.)
        v.name = "web#{i}"
        v.memory = RAM_MB
        v.cpus = CORE_COUNT
      end
      server.vm.network "private_network", ip: "192.168.99.#{i+10}"

      server.vm.network :forwarded_port, guest: 22, host: 10122
      server.vm.synced_folder "./app", "/app", type: "nfs"
      # server.vm.provision "shell", path: "script_on_host.sh"
      server.vm.provision "shell", inline: $web_script
    end
  end

    config.vm.define "db" do |db|
    db.vm.box = "precise64"
    db.vm.hostname = 'db'
    db.vm.box_url = "ubuntu/precise64"

    db.vm.network :private_network, ip: "192.168.56.102"
    db.vm.network :forwarded_port, guest: 22, host: 10222, id: "ssh"

    db.vm.provider :virtualbox do |v|
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 512]
      v.customize ["modifyvm", :id, "--name", "db"]
    end

    db.vm.provision "shell", inline: $db_script
  end

end