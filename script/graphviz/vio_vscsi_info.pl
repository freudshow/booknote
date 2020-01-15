#!/usr/bin/perl
#  This is unsupported code.  This script is provided "as is" without warranty of
#  any kind, expressed or implied, including, but not limited to, the implied
#  warranty of merchantability or fitness for a particular purpose.
#  Use at your own risk.

use strict;
use Switch;

my $hmc_server_name = "";
my $system;
my @output;
my @output2;
my ($system_status,$line,$line2,$system);

if ($#ARGV + 1 == 2 ) {
  $hmc_server_name = $ARGV[0];
  $system = $ARGV[1];
}else{
  print "Specify HMC name and managed system names as arguments\n";
  exit 1;
}

my %vioservers;
my $vioserver_count = 0;

print "graph vscsi_graph {\n";
print "nodesep=.75\n";
print "ranksep=2\n";

my %vio_slots;

@output = `ssh -q -o "BatchMode yes" $hmc_server_name 'lshwres -r virtualio --rsubtype scsi -m $system -F lpar_name,lpar_id,slot_num,adapter_type,remote_lpar_id,remote_slot_num,remote_lpar_name | sort'`;
foreach $line (@output){
  my ($lpar_name,$lpar_id,$slot_num,$adapter_type);
  my ($remote_lpar_id,$remote_slot_num,$remote_lpar_name);
  if ($line =~ /(\S+),(\d+),(\d+),(\S+),(\d+),(\d+),(\S+)/){
    my $vio = $1;
    my $lpar_id = $2;
    my $slot_num = $3;
    my $adapter_type = $4;
    my $remote_lpar_id = $5;
    my $remote_slot_num = $6;
    my $lpar = $7;
    if ($adapter_type eq "server"){       #We are only interested in server adapters
      if ( ! grep(/$vio/, %vioservers)) {
        $vioserver_count++;
        my $vio_color = "red";
        switch($vioserver_count){
          case 1 {$vio_color = "#A9A9A9";}
          case 2 {$vio_color = "#97B7E1";}
        }
        push(@{$vioservers{$vio}}, $vio_color);
        push(@{$vioservers{$vio}}, $vioserver_count);

        %vio_slots = ();
        @output2 = `ssh -q -o "BatchMode yes" $hmc_server_name "viosvrcmd -m $system -p $vio -c 'lsdev -slots'"`;
        foreach $line2 (@output2){
          if ($line2 =~ /^\S+-C(\d+)\s+.*(vhost\d+)/){
            my $slot = $1;
            my $vhost = $2;
            my $key = "$vio.$slot";
            push(@{$vio_slots{$key}}, $vhost);
          }
        }
      }

      my $key = "$vio.$slot_num";
      if (@{$vioservers{$vio}}[1] % 2 ne 0) {
        print "\"$vio\" -- \"$vio.@{$vio_slots{$key}}[0]\" [color=\"@{$vioservers{$vio}}[0]\", weight=200];\n";
        print "\"$vio.@{$vio_slots{$key}}[0]\" -- \"$lpar.$remote_slot_num\" [color=\"@{$vioservers{$vio}}[0]\", weight=200];\n";
        print "\"$lpar.$remote_slot_num\" -- \"$lpar\" [color=\"@{$vioservers{$vio}}[0]\", weight=200];\n";
      }else{
        print "\"$lpar\" -- \"$lpar.$remote_slot_num\" [color=\"@{$vioservers{$vio}}[0]\", weight=200];\n";
        print "\"$lpar.$remote_slot_num\" -- \"$vio.@{$vio_slots{$key}}[0]\" [color=\"@{$vioservers{$vio}}[0]\", weight=200];\n";
        print "\"$vio.@{$vio_slots{$key}}[0]\" -- \"$vio\" [color=\"@{$vioservers{$vio}}[0]\", weight=200];\n";
      }

      print "\"$vio\" [label=\"$vio\", color=\"@{$vioservers{$vio}}[0]\", fontsize=16,fontcolor=black,style=filled];\n";
      print "\"$vio.@{$vio_slots{$key}}[0]\" [label=\"Virtual SCSI\\nServer Adapter\\n@{$vio_slots{$key}}[0]\\nSlot $slot_num\", color=\"@{$vioservers{$vio}}[0]\", fontsize=16,fontcolor=black,style=filled];\n";
      print "\"$lpar.$remote_slot_num\" [label=\"Virtual SCSI\\nClient Adapter\\nSlot $remote_slot_num\", color=\"@{$vioservers{$vio}}[0]\", fontsize=16,fontcolor=black,style=filled];\n";
      my $client_color="#FFF999";
      if ($lpar eq "null") { $client_color="#FF0000"; }
      print "\"$lpar\" [shape=box, label=\"$lpar\", color=\"$client_color\", fontsize=16,fontcolor=black,style=filled];\n";
    }
  }
}
print "}\n";
