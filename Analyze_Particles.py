import os
import time
import re
from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import FileSaver
from ij.plugin import ZProjector
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer
from loci.formats import ImageReader, MetadataTools
from ij.measure import ResultsTable


startTime = [time.strftime("%a, %d %b %Y %H:%M:%S"), time.time()]
imageCount=0
## The following lines are the settings for particle size and circularity, change if needed
particle_size_min = 150
particle_size_max = "Infinity"
particle_circ_min = 0.00
particle_circ_max = 1.00

particle_size = str(particle_size_min) + "-" + str(particle_size_max)
particle_circ = str(particle_circ_min) + "-" + str(particle_circ_max)

in_dir = IJ.getDirectory("Choose Directory Containing Input Files (ND2)")
out_dir = IJ.getDirectory("Choose Directory For Output")

def saveImage(img, out_file):
	FileSaver(img).saveAsTiff(out_file)

def maxZprojection(stackimp):
	zp = ZProjector(stackimp)
	zp.setMethod(ZProjector.MAX_METHOD)
	zp.doProjection()
	zpimp = zp.getProjection()
	return zpimp
	
for root, dirs, files in os.walk(in_dir):
	for file in files:
		if file.endswith(".nd2"):
			options = ImporterOptions()
			options.setAutoscale(True)
			options.setId(os.path.join(root, file))
			options.setSplitChannels(True)
			imps = BF.openImagePlus(options)
			for imp in imps:
				reader = ImageReader()
				omeMeta = MetadataTools.createOMEXMLMetadata()
				reader.setMetadataStore(omeMeta)
				reader.setId(os.path.join(root, file))
				
				filename = str(imp)
				channel_id = int(re.findall("C=(\d)", filename)[0])
				channel_name = omeMeta.getChannelName(0, channel_id)
				# only processes TRITC channel
				if channel_name == 'TRITC':
					out_name = filename.split('"')[1]
					out_name = out_name.split(".nd2")[0] + "_" + str(channel_name)
					out_name = out_name.replace(" ", "")
					'''
					open nd2 with split channels
					for TRITC channel: max Intensity projection
					run AutoThreshold with Default method
					run Watershed to separate overlaying particles
					run analyze particles with defined settings

					'''
					zimp = maxZprojection(imp)
					IJ.run(zimp, "Auto Threshold", "method=Default white")
					IJ.run(zimp, "Watershed", "")
					IJ.run(zimp, "Analyze Particles...", "size=" + str(particle_size) + " circularity=" + str(particle_circ) + " show=Outlines display exclude summarize add")
					zimp2 = zimp.flatten();
					saveImage(zimp2, os.path.join(out_dir, out_name + ".tiff"))
					drawing_name = "Drawing of " + str(zimp).split('"')[1]
					IJ.selectWindow(drawing_name)
					IJ.saveAs("Tiff", os.path.join(out_dir, out_name + "_drawing.tiff"))
					IJ.run("Close")
					IJ.selectWindow("Results")
					IJ.saveAs("Results", os.path.join(out_dir, out_name + ".csv"))
					IJ.run("Clear Results", "")
					IJ.selectWindow("ROI Manager")
					IJ.run("Close")			
					imageCount += 1
					
IJ.selectWindow("Summary")
IJ.saveAs("Results", os.path.join(out_dir, "Summary.csv"))

				