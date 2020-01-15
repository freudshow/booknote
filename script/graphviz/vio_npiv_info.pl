#!/usr/bin/perl
#  This is unsupported code.  This script is provided "as is" without warranty of
#  any kind, expressed or implied, including, but not limited to, the implied
#  warranty of merchantability or fitness for a particular purpose.
#  Use at your own risk.


use strict;
my @output;
my @lpar_list;
my %dup_check_hash;
my $managed_system = "";
my $hmc_server_name = "";
my ($system_status, $lpar_info, $outputline, $vio_count);

if ($#ARGV + 1 == 2 ) {
    $hmc_server_name = $ARGV[0];
    $managed_system = $ARGV[1];
}else{
    print "Specify HMC name and managed system name as arguments\n";
    exit 1;
}

print "graph NPIV_Diagram { \n";
print "nodesep=.5\n";
print "ranksep=.5\n";
print "rankdir=LR\n";

@lpar_list = `ssh -q -o "BatchMode yes" $hmc_server_name 'lssyscfg -m $managed_system -r lpar -F "name,lpar_env,state" | sort'`;
foreach $lpar_info (@lpar_list){
  if ($lpar_info =~ /(\S+),(\S+),(.*)/){
    my $vio_server = $1;
    my $client_type = $2;
    my $client_state = $3;
    if ($client_state eq "Running" && $client_type eq "vioserver"){
      $vio_count++;
      @output = `ssh -q -o "BatchMode yes" $hmc_server_name "viosvrcmd -m $managed_system -p $vio_server -c 'lsmap -all -npiv -field name physloc clntname fc fcphysloc vfcclient vfcclientdrc -fmt ,'"`;
      foreach $outputline (@output){
        if ($outputline =~ /(\S+),.*-C(\d+),([^,]*),(\S+),(\S+),(\S+),.*-C(\d+)/){
          my $vfchost = $1;
          my $slot = $2;
          my $clntname = $3;
          my $fc = $4;
          my $fcphsloc = $5;
          my $vfcclient = $6;
          my $vfcclientdrs = $7;
          if ($vio_count % 2 ne 0) {
            print_if_not_dup("\"${vio_server}\" -- \"${vio_server}.${fc}\"");
            print_if_not_dup("\"${vio_server}.${fc}\" -- \"${vio_server}.${vfchost}\"");
            print_if_not_dup("\"${vio_server}.${vfchost}\" -- \"${clntname}.${vfcclient}\"");
            print_if_not_dup("\"${clntname}.${vfcclient}\" -- \"${clntname}\"");
          }else{
            print_if_not_dup("\"${clntname}\" -- \"${clntname}.${vfcclient}\"");
            print_if_not_dup("\"${clntname}.${vfcclient}\" -- \"${vio_server}.${vfchost}\"");
            print_if_not_dup("\"${vio_server}.${vfchost}\" -- \"${vio_server}.${fc}\"");
            print_if_not_dup("\"${vio_server}.${fc}\" -- \"${vio_server}\"");
          }
          print_if_not_dup("\"${clntname}\" [shape=Mrecord, label=\"${clntname}|LPAR\", fillcolor=\"#97B7E1\", fontsize=10,fontcolor=black,style=filled]");
          print_if_not_dup("\"${vio_server}\" [shape=Mrecord, label=\"${vio_server}|VIO Server\", fillcolor=\"#97B7E1\", fontsize=10,fontcolor=black,style=filled]");
          print_if_not_dup("\"${vio_server}.${vfchost}\" [shape=Mrecord, label=\"Virt Fibre Srv Adp|VIO Slot $slot | $vfchost\",fillcolor=\"#97B7E1\" , fontsize=10,fontcolor=black,style=filled]");
          print_if_not_dup("\"${clntname}.${vfcclient}\" [shape=Mrecord, label=\"Virt Client HBA|Client Slot $vfcclientdrs|Client Device: $vfcclient\", fillcolor=\"#A9A9A9\", fontsize=10,fontcolor=black,style=filled]");
          print_if_not_dup("\"${vio_server}.${fc}\" [shape=Mrecord, label=\"Physical VIO HBA|$fc|$fcphsloc\", fillcolor=\"#A9A9A9\", fontsize=10,fontcolor=black,style=filled]");
        }
      }
    }
  }
}

print "}\n";

sub print_if_not_dup{
  my $string = $_[0];
  if (! grep /\Q$string/, %dup_check_hash){
    print "$string\n";
    $dup_check_hash{$string} = "";
  }
}
