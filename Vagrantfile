# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end

  config.vm.provision :shell, path: "scripts/bootstrap.sh"

  config.vm.network "forwarded_port", guest: 8000, host: 8080 # Application
  config.vm.network "forwarded_port", guest: 5432, host: 5432 # Database
end
