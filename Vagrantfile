# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "chef/debian-7.4"
  config.ssh.forward_agent = true
  config.vm.synced_folder ".", "/vagrant", type: "rsync",
      rsync__args: ["--verbose", "--archive", "-z"]
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
  end
end
