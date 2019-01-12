#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.fsl as fsl
import nipype.interfaces.utility as utility

#Generic datagrabber module that wraps around glob in an
my_io_S3DataGrabber = pe.Node(io.S3DataGrabber(outfields=["outfiles"]), name = 'my_io_S3DataGrabber')
my_io_S3DataGrabber.inputs.bucket = 'openneuro'
my_io_S3DataGrabber.inputs.sort_filelist = True
my_io_S3DataGrabber.inputs.template = 'sub-01/anat/sub-01_T1w.nii.gz'
my_io_S3DataGrabber.inputs.anon = True
my_io_S3DataGrabber.inputs.bucket_path = 'ds000101/ds000101_R2.0.0/uncompressed/'
my_io_S3DataGrabber.inputs.local_directory = '/tmp'

#Wraps command **bet**
my_fsl_BET = pe.Node(interface = fsl.BET(), name='my_fsl_BET', iterfield = [''])

#Change the name of a file based on a mapped format string.
my_utility_Rename = pe.Node(interface = utility.Rename(), name='my_utility_Rename', iterfield = [''])
my_utility_Rename.inputs.format_string = "/output/skullstrip.nii.gz"

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(my_io_S3DataGrabber, "outfiles", my_fsl_BET, "in_file")
analysisflow.connect(my_fsl_BET, "out_file", my_utility_Rename, "in_file")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
