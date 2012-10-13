#!/usr/bin/env python
#
# Copyright (c) 2012 by John Chiu
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# --- Change Log ---------------------------------------------------
# 0.1 
#	- Add initial working file.
# ------------------------------------------------------------------

__author__ = 'johnkchiu@yahoo.com (John Chiu)'
__script_name__ = '%prog'
__version__ = '0.1'

import json
import os
from optparse import OptionParser
from smugpy import SmugMug, SmugMugException

def print_json(object):
	print json.dumps(object, sort_keys=True, indent=4)

if __name__ == '__main__':
	# read arguments
	usage = """
	Commandline tool for Smugmug.
		%prog [option]
	"""
	parser = OptionParser(usage=usage, version=__script_name__+' '+__version__)
	parser.add_option('-a', action='store', dest='api_key', help='Smugmug API Key')
	parser.add_option('-e', action='store', dest='email', help='Login email')
	parser.add_option('-p', action='store', dest='password', help='Login password')
	parser.add_option('-t', action='store', dest='template', help='Template name')
	parser.add_option('-c', action='store', dest='category', help='Category name')
	parser.add_option('-s', action='store', dest='subcategory', help='Sub-Category name')
	parser.add_option('-f', action='store', dest='folder', help='Folder to upload from (should not have "/" at the end.')
	(options, args) = parser.parse_args()
	print(options)

	# using the old API (1.2.2), which is easier to use for one shot scripts (avoids OAuth)
	smugmug = SmugMug(api_key=options.api_key, api_version="1.2.2", app_name=__script_name__)

	# test login
	smugmug.login_withPassword(EmailAddress=options.email, Password=options.password)

	# find template id by name
	response = smugmug.albumtemplates_get()
	for template in response['AlbumTemplates']:
		if template['AlbumTemplateName'] == options.template:
			templateId = template['id']
	print_json(templateId)

	# find category id by name
	response = smugmug.categories_get()
	for category in response['Categories']:
		if category['Name'] == options.category:
			categoryId = category['id']
	print_json(categoryId)

	# find subcategory id by name
	response = smugmug.subcategories_get(CategoryID=categoryId)
	for subcategory in response['SubCategories']:
		if subcategory['Name'] == options.subcategory:
			subcategoryId = subcategory['id']
	print_json(subcategoryId)

	# create ablum
	title = os.path.basename(options.folder)
	response = smugmug.albums_create(AlbumTemplateID=templateId, CategoryID=categoryId, SubCategoryID=subcategoryId, Title=title)
	album = response['Album']
	print_json(album)

	# go thru folder and upload
	for root, subfolders, files in os.walk(options.folder):
		for file in files:
			try:
				filename = os.path.join(root,file)
				print_json(filename)
				response = smugmug.images_upload(File=filename, AlbumID=album['id'])
				print_json(response)
			except SmugMugException as e:
				print e

