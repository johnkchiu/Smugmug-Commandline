#!/usr/bin/env python
#
# ------------------------------------------------------------------
# Copyright (c) 2012 by John Chiu
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this filename except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# ------------------------------------------------------------------

__author__ = 'johnkchiu@yahoo.com (John Chiu)'
__script_name__ = '%prog'
__version__ = '0.1.1'

from optparse import OptionParser
from smugpy import SmugMug, SmugMugException
import json
import os

class SmugMugCommandLine(object):

	def __init__(self, api_key=None, email=None, password=None):
		"""initalize class"""
		self.api_key = api_key
		self.email = email
		self.password = password
		# using the old API (1.2.2), which is easier to use for one shot scripts (avoids OAuth)
		self.smugmug = SmugMug(api_key=options.api_key, api_version="1.2.2", app_name=__script_name__)
		# login
		self.smugmug.login_withPassword(EmailAddress=options.email, Password=options.password)
	
	def template_get(self, template_name=None):
		"""find template by name"""
		response = self.smugmug.albumtemplates_get()
		for template in response['AlbumTemplates']:
			if template['AlbumTemplateName'] == template_name:
				return template
		return None

	def category_get(self, category_name=None):
		"""find category by name"""
		response = self.smugmug.categories_get()
		for category in response['Categories']:
			if category['Name'] == category_name:
				return category
		return None

	def subcategory_get(self, subcategory_name=None):
		"""find subcategory by name"""
		response = self.smugmug.subcategories_get(CategoryID=self.category['id'])
		for subcategory in response['SubCategories']:
			if subcategory['Name'] == subcategory_name:
				return subcategory
		return None

	def album_get(self, album_name=None):
		"""find album by name"""
		response = self.smugmug.albums_get()
		for album in response['Albums']:
			if album['Title'] == album_name:
				return album
		return None

	def album_getInfo(self, album_id=None, album_key=None):
		"""get album info"""
		response = self.smugmug.albums_getInfo(AlbumID=album_id, AlbumKey=album_key)
		album = response['Album']
		return album

	def album_create(self, title=None, category_id=None, subcategory_id=None, album_template_id=None):
		"""create ablum"""
		response = self.smugmug.albums_create(AlbumTemplateID=album_template_id, CategoryID=category_id, SubCategoryID=subcategory_id, Title=title)
		album = response['Album']
		return album
	
	def images_getInfo(self, image_id=None, image_key=None):
		"""get image info"""
		response = self.smugmug.images_getInfo(ImageID=image_id, ImageKey=image_key)
		image_info = response['Image']
		return image_info
		
	def images_get(self, album_id=None, album_key=None):
		"""get all image for an ablum"""
		response = self.smugmug.images_get(AlbumID=album_id, AlbumKey=album_key)
		images = response['Album']['Images']
		return images	
	
	def images_get_filenames(self, album_id=None, album_key=None):
		"""get all images for an ablum as a collection of filenames"""
		filename_list = list()
		images = self.images_get(album_id=album_id, album_key=album_key)
		for image in images:
			image_info = self.images_getInfo(image_id=image['id'], image_key=image['Key'])
			filename_list.append(image_info['FileName'])
		return filename_list


def print_json(obj):
	print json.dumps(obj, sort_keys=True, indent=4)
	
def log_image_status(filename=None, status=None):
	print "File: " + filename + "\t\t Status: " + status

def exit_with_error(message=None):
	print message
	exit(1)

if __name__ == '__main__':
	# read arguments
	usage = """
	Commandline tool for Smugmug.
		%prog [option]
	"""
	parser = OptionParser(usage=usage, version=__script_name__ + " " + __version__)
	parser.add_option('-a', action='store', dest='api_key', help='Smugmug API Key')
	parser.add_option('-e', action='store', dest='email', help='Login email')
	parser.add_option('-p', action='store', dest='password', help='Login password')
	parser.add_option('-t', action='store', dest='template', help='Template name')
	parser.add_option('-c', action='store', dest='category', help='Category name')
	parser.add_option('-s', action='store', dest='subcategory', help='Sub-Category name (Optional)')
	parser.add_option('-f', action='store', dest='folder', help='Folder to upload from (should not have "/" at the end.')
	(options, args) = parser.parse_args()

	# create instance
	smcl = SmugMugCommandLine(api_key=options.api_key, email=options.email, password=options.password)

	# get or create album
	album_title = os.path.basename(options.folder)
	album = smcl.album_get(album_name=album_title)
	if album is not None:
		# album exists
		album_info = smcl.album_getInfo(album_id=album['id'], album_key=album['Key'])
		print "Album exist: " + album_info['URL']
	else:
		# create album
		template = smcl.template_get(options.template)
		category = smcl.category_get(options.category)
		if options.subcategory is not None:
			subcategory = smcl.subcategory_get(options.subcategory)
			album = smcl.album_create(title=album_title, category_id=category['id'], subcategory_id=subcategory['id'], album_template_id=template['id'])
		else:
			album = smcl.album_create(title=album_title, category_id=category['id'], album_template_id=template['id'])
		album_info = smcl.album_getInfo(album_id=album['id'], album_key=album['Key'])
		print "Album created: " + album_info['URL']
	if album is None:
		# then it's a problem
		exit_with_error("Album NOT found or created")

	# upload pictures
	file_total = 0;
	file_upload = 0;
	file_exist = 0;
	file_error = 0;
	album_files  = smcl.images_get_filenames(album_id=album['id'], album_key=album['Key'])
	for root, subfolders, files in os.walk(options.folder):
		for filename in files:
			file_total += 1
			# check for filename
			if filename in album_files:
				# file exits
				log_image_status(filename=filename, status="Exist")
				file_exist += 1
			else:
				# upload file
				try:
					filepath = os.path.join(root, filename)
					response = smcl.smugmug.images_upload(File=filepath, AlbumID=album['id'])
					log_image_status(filename=filename, status="Uploaded")
					file_upload += 1
				except SmugMugException as e:
					log_image_status(filename=filename, status="Error (" + str(e) + ")")
					file_error += 1
		# stop after 1 level
		break
	
	# all done
	print "Complete (Total:" + str(file_total) + ", Uploaded:" + str(file_upload) + \
	 		", Exits:" + str(file_exist) + ", Failed:" + str(file_error) + ")"
	exit(0)
