#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.fsl as fsl

#Generic datagrabber module that wraps around glob in an
data_from_openneuro = pe.Node(io.S3DataGrabber(outfields=["outfiles"]), name = 'data_from_openneuro')
data_from_openneuro.inputs.bucket = 'openneuro'
data_from_openneuro.inputs.sort_filelist = True
data_from_openneuro.inputs.template = 'sub-01/anat/sub-01_T1w.nii.gz'
data_from_openneuro.inputs.anon = True
data_from_openneuro.inputs.bucket_path = 'ds000101/ds000101_R2.0.0/uncompressed/'
data_from_openneuro.inputs.local_directory = '/tmp'

#Wraps command **bet**
brain_extraction = pe.Node(interface = fsl.BET(), name='brain_extraction', iterfield = [''])

#Generic datasink module to store structured outputs
save_data = pe.Node(interface = io.DataSink(), name='save_data', iterfield = [''])
save_data.inputs.base_directory = '/tmp'

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(data_from_openneuro, "outfiles", brain_extraction, "in_file")
analysisflow.connect(brain_extraction, "out_file", save_data, "BET_results")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
