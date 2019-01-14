#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.fsl as fsl
import nipype.interfaces.utility as utility

#Generic datagrabber module that wraps around glob in an
anat_from_openneuro = pe.Node(io.S3DataGrabber(outfields=["anat"]), name = 'anat_from_openneuro')
anat_from_openneuro.inputs.bucket = 'openneuro'
anat_from_openneuro.inputs.sort_filelist = True
anat_from_openneuro.inputs.template = 'sub-01/anat/sub-01_T1w.nii.gz'
anat_from_openneuro.inputs.anon = True
anat_from_openneuro.inputs.bucket_path = 'ds000101/ds000101_R2.0.0/uncompressed/'
anat_from_openneuro.inputs.local_directory = '/tmp'

#Wraps command **bet**
brain_extraction = pe.Node(interface = fsl.BET(), name='brain_extraction', iterfield = [''])

#Generic datagrabber module that wraps around glob in an
func_from_openneuro = pe.Node(io.S3DataGrabber(outfields=["func"]), name = 'func_from_openneuro')
func_from_openneuro.inputs.bucket = 'openneuro'
func_from_openneuro.inputs.sort_filelist = True
func_from_openneuro.inputs.template = 'sub-01/func/sub-01_task-simon_run-1_bold.nii.gz'
func_from_openneuro.inputs.anon = True
func_from_openneuro.inputs.bucket_path = 'ds000101/ds000101_R2.0.0/uncompressed/'
func_from_openneuro.inputs.local_directory = '/tmp'

#Change the name of a file based on a mapped format string.
utility_Rename = pe.Node(interface = utility.Rename(), name='utility_Rename', iterfield = [''])
utility_Rename.inputs.format_string = "/output/registered.nii.gz"

#Wraps command **flirt**
fsl_FLIRT = pe.Node(interface = fsl.FLIRT(), name='fsl_FLIRT', iterfield = [''])

#Wraps command **mcflirt**
fsl_MCFLIRT = pe.Node(interface = fsl.MCFLIRT(), name='fsl_MCFLIRT', iterfield = [''])

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(anat_from_openneuro, "anat", brain_extraction, "in_file")
analysisflow.connect(func_from_openneuro, "func", fsl_MCFLIRT, "in_file")
analysisflow.connect(brain_extraction, "out_file", fsl_FLIRT, "in_file")
analysisflow.connect(fsl_MCFLIRT, "out_file", fsl_FLIRT, "reference")
analysisflow.connect(fsl_FLIRT, "out_file", utility_Rename, "in_file")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
