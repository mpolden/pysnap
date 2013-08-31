# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
  set -x

  # Ensure noninteractive apt-get
  export DEBIAN_FRONTEND=noninteractive

  # Set time zone
  echo "Europe/Oslo" > /etc/timezone
  dpkg-reconfigure tzdata

  # Install packages
  apt-get -y --quiet update
  apt-get -y --quiet install make python-pip

  # Install pip packages
  pip install --quiet --upgrade -r /vagrant/requirements.txt \
          -r /vagrant/dev-requirements.txt
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "raring64-current"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
  config.ssh.forward_agent = true
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
  config.vm.provision :shell, :inline => $script
end
