import hashlib, base64, requests, json, os
try:
	from boto.s3.connection import S3Connection
	from boto.s3.bucket import Bucket as S3Bucket
	from boto.s3.key import Key as S3Key
except Exception, e:
	raise Exception("Could not import amazon's boto toolkit.  If it is not installed, follow the instructions on https://aws.amazon.com/sdkforpython/")


class Volar(object):
	"""
	SDK for interfacing with the Volar cms.  Allows pulling of lists as well
	as manipulation of records.  Requires an api user to be set up.  All
	requests (with the exception of the Volar.sites call) requires the 'site'
	parameter, and 'site' much match the slug value of a site that the given
	api user has access to.  Programmers can use the Volar.sites call to get
	this information.
	depends on the requests module:
		http://docs.python-requests.org/en/latest/user/install/#install
	"""

	def __init__(self, api_key, secret, base_url):
		self.api_key = api_key
		self.secret = secret
		self.base_url = base_url
		self.secure = False
		self.error = ''

	def sites(self, params = {}):
		"""
		gets list of sites

		@param dict params
			- optional -
			'list' : type of list.  allowed values are 'all', 'archived',
				'scheduled' or 'upcoming', 'upcoming_or_streaming',
				'streaming' or 'live'
			'page': current page of listings.  pages begin at '1'
			'per_page' : number of broadcasts to display per page
			'section_id' : id of section you wish to limit list to
			'playlist_id' : id of playlist you wish to limit list to
			'id' : id of site - useful if you only want to get details
				of a single site
			'slug' : slug of site.  useful for searches, as this accepts
				incomplete titles and returns all matches.
			'title' : title of site.  useful for searches, as this accepts
				incomplete titles and returns all matches.
			'sort_by' : data field to use to sort.  allowed fields are date,
				status, id, title, description
			'sort_dir' : direction of sort.  allowed values are 'asc'
				(ascending) and 'desc' (descending)
		@return false on failure, dict on success.  if failed, Volar.error can
			be used to get last error string
		"""

		return self.request(route = 'api/client/info', method = 'GET', params = params)

	def broadcasts(self, params = {}):
		"""
		gets list of broadcasts

		@param dict params
			- required -
			'site' OR 'sites'	slug of site to filter to.
				if passing 'sites', users can include a comma-delimited list of
				sites.  results will reflect all broadcasts in the listed
				sites.
			- optional -
			'list' : type of list.  allowed values are 'all', 'archived', 
				'scheduled' or 'upcoming', 'upcoming_or_streaming',
				'streaming' or 'live'
			'page' : current page of listings.  pages begin at '1'
			'per_page' : number of broadcasts to display per page
			'section_id' : id of section you wish to limit list to
			'playlist_id' : id of playlist you wish to limit list to
			'id' : id of broadcast - useful if you only want to get details
				of a single broadcast
			'title' : title of broadcast.  useful for searches, as this
				accepts incomplete titles and returns all matches.
			'template_data' : dict.  search broadcast template data.  should
				be in the form:
					{
						'field title' : 'field value',
						'field title' : 'field value',
						....
					}
			'autoplay' : true or false.  defaults to false.  used in embed
				code to prevent player from immediately playing
			'embed_width' : width (in pixels) that embed should be.  defaults
				to 640
			'sort_by' : data field to use to sort.  allowed fields are date,
				status, id, title, description
			'sort_dir' : direction of sort.  allowed values are 'asc'
				(ascending) and 'desc' (descending)
		@return false on failure, dict on success.  if failed, Volar.error can
			be used to get last error string
		"""

		if(('site' not in params) and ('sites' not in params)):
			self.error = '"site" or "sites" parameter is required'
			return False
		return self.request(route = 'api/client/broadcast', params = params)

	def broadcast_create(self, params = {}):
		"""
		create a new broadcast

		@param dict params
			- required -
			'title' : title of the new broadcast
			'contact_name' : contact name of person we should contact if we detect problems with this broadcast
			'contact_phone' : phone we should use to contact contact_name person
			'contact_sms' : sms number we should use to send text messages to contact_name person
			'contact_email' : email address we should use to send emails to contact_name person
				* note that contact_phone can be omitted if contact_sms is supplied, and vice-versa
			- optional -
			'description' : HTML formatted description of the broadcast.
			'status' : currently only supports 'scheduled' & 'upcoming'
			'timezone' : timezone of given date.  only timezones listed
				on http://php.net/manual/en/timezones.php are supported.
				defaults to UTC
			'date' : date (string) of broadcast event.  will be converted
				to UTC if the given timezone is given.  note that if the
				system cannot read the date, or if it isn't supplied, it
				will default it to the current date & time.
			'section_id' : id of the section that this broadcast should
				be assigned.  the Volar.sections() call can give you a
				list of available sections.  Defaults to a 'General' section
		@return dict
			{
				'success' : True or False depending on success
				...
				if 'success' == True:
					'broadcast' : dict containing broadcast information,
						including id of new broadcast
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/broadcast/create', method = 'POST', params = { 'site' : site }, post_body = params)

	def broadcast_update(self, params = {}):
		"""
		update existing broadcast

		@param dict params
			- required -
			'id' : id of broadcast you wish to update
			- optional -
			'title' : title of the new broadcast.  if supplied, CANNOT be
				blank
			'description' : HTML formatted description of the broadcast.
			'status' : currently only supports 'scheduled' & 'upcoming'
			'timezone' : timezone of given date.  only timezones listed
				on http://php.net/manual/en/timezones.php are supported.
				defaults to UTC
			'date' : date (string) of broadcast event.  will be converted
				to UTC if the given timezone is given.  note that if the
				system cannot read the date, or if it isn't supplied, it
				will default it to the current date & time.
			'section_id' : id of the section that this broadcast should
				be assigned.  the Volar.sections() call can give you a
				list of available sections.  Defaults to a 'General' section
			'contact_name' : contact name of person we should contact if we detect problems with this broadcast
			'contact_phone' : phone we should use to contact contact_name person
			'contact_sms' : sms number we should use to send text messages to contact_name person
			'contact_email' : email address we should use to send emails to contact_name person
				* note that contact_phone can be omitted if contact_sms is supplied, and vice-versa
		@return dict
			{
				'success' : True or False depending on success
				if 'success' == True:
					'broadcast' : dict containing broadcast information,
						including id of new broadcast
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/broadcast/update', method = 'POST', params = { 'site' : site }, post_body = params)

	def broadcast_delete(self, params = {}):
		"""
		delete a broadcast

		the only parameter (aside from 'site') that this function takes is 'id'
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/broadcast/delete', method = 'POST', params = { 'site' : site }, post_body = params)

	def broadcast_assign_playlist(self, params = {}):
		"""
		assign a broadcast to a playlist

		@params dict params
			'id' : id of broadcast
			'playlist_id' : id of playlist
		@return dict { 'success' : True }
		"""
		if('site' not in params):
			self.error = 'site is required'
			return False
		return self.request(route = 'api/client/broadcast/assignplaylist', params = params)

	def broadcast_remove_playlist(self, params = {}):
		"""
		remove a broadcast from a playlist

		@params dict params
			'id' : id of broadcast
			'playlist_id' : id of playlist
		@return dict { 'success' : True }
		"""
		if('site' not in params):
			self.error = 'site is required'
			return False
		return self.request(route = 'api/client/broadcast/removeplaylist', params = params)

	def broadcast_poster(self, params = {}, file_path = '', filename = ''):
		"""
		uploads an image file as the poster for a broadcast.

		@params
			dict params
				'id' : id of broadcast
			string file_path
				if supplied, this file is uploaded to the server and attached
				to the broadcast as an image
			string filename
				if supplied & file_path is also given, the uploaded file's
				name is reported to Volar as this filename.  used for easing
				file upload passthrus.  if not supplied, the filename from
				file_path is used.
		@return dict
			{
				'success' : True or False depending on success
				if 'success' == False:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		if file_path == '':
			return self.request(route = 'api/client/broadcast/poster', method = 'GET', params = params)
		else:
			if filename != '':
				post = {'files' : { 'api_poster': (filename, open(file_path, 'rb'))}}
			else:
				post = {'files' : { 'api_poster': open(file_path, 'rb')}}
			return self.request(route = 'api/client/broadcast/poster', method = 'POST', params = params, post_body = post)

	def broadcast_archive(self, params = {}, file_path = ''):
		"""
		archives a broadcast.

		@params
			dict params
				'id' : id of broadcast
				'site' : slug of site that broadcast is attached to.
			string file_path
				if supplied, this file is uploaded to the server and attached
				to the broadcast
		@return dict
			{
				'success' : True or False depending on success
				'broadcast' : dict describing broadcast that was modified.
				if 'success' == True:
					'fileinfo' : dict containing information about the
					uploaded file (if there was a file uploaded)
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		if file_path == '':
			return self.request(route = 'api/client/broadcast/archive', method = 'GET', params = params)
		else:
			fileParams = self.upload_file(file_path)
			if fileParams == False:
				return False
			else:
				for key, value in fileParams.iteritems():
					params[key] = value
			return self.request(route = 'api/client/broadcast/archive', method = 'GET', params = params)

	def videoclips(self, params = {}):
		"""
		gets list of videoclips

		@param dict params
			- required -
			'site' OR 'sites'	slug of site to filter to.
				if passing 'sites', users can include a comma-delimited list of
				sites.  results will reflect all videoclips in the listed
				sites.
			- optional -
			'page' : current page of listings.  pages begin at '1'
			'per_page' : number of videoclips to display per page
			'section_id' : id of section you wish to limit list to
			'playlist_id' : id of playlist you wish to limit list to
			'id' : id of videoclip - useful if you only want to get details
				of a single videoclip
			'title' : title of videoclip.  useful for searches, as this
				accepts incomplete titles and returns all matches.
			'autoplay' : true or false.  defaults to false.  used in embed
				code to prevent player from immediately playing
			'embed_width' : width (in pixels) that embed should be.  defaults
				to 640
			'sort_by' : data field to use to sort.  allowed fields are date,
				status, id, title, description
			'sort_dir' : direction of sort.  allowed values are 'asc'
				(ascending) and 'desc' (descending)
		@return false on failure, dict on success.  if failed, Volar.error can
			be used to get last error string
		"""

		if(('site' not in params) and ('sites' not in params)):
			self.error = '"site" or "sites" parameter is required'
			return False
		return self.request(route = 'api/client/videoclip', params = params)

	def videoclip_create(self, params = {}):
		"""
		create a new videoclip

		@param dict params
			- required -
			'site':	slug of site to attach videoclip to
			'title' : title of the new videoclip
			- optional -
			'description' : HTML formatted description of the videoclip.
			'section_id' : id of the section that this videoclip should
				be assigned.  the Volar.sections() call can give you a
				list of available sections.  Defaults to a 'General' section
		@return dict
			{
				'success' : True or False depending on success
				...
				if 'success' == True:
					'clip' : dict containing videoclip information,
						including id of new videoclip
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/videoclip/create', method = 'POST', params = { 'site' : site }, post_body = params)

	def videoclip_update(self, params = {}):
		"""
		update existing videoclip

		@param dict params
			- required -
			'site':	slug of site that id is attached to
			'id' : id of videoclip you wish to update
			- optional -
			'title' : title of the new videoclip.  if supplied, CANNOT be
				blank
			'description' : HTML formatted description of the videoclip.
			'section_id' : id of the section that this videoclip should
				be assigned.  the Volar.sections() call can give you a
				list of available sections.  Defaults to a 'General' section
		@return dict
			{
				'success' : True or False depending on success
				if 'success' == True:
					'clip' : dict containing videoclip information,
						including id of new videoclip
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/videoclip/update', method = 'POST', params = { 'site' : site }, post_body = params)

	def videoclip_delete(self, params = {}):
		"""
		delete a videoclip

		the only parameter (aside from 'site') that this function takes is 'id'
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/videoclip/delete', method = 'POST', params = { 'site' : site }, post_body = params)

	def videoclip_assign_playlist(self, params = {}):
		"""
		assign a videoclip to a playlist

		@params dict params
			'id' : id of videoclip
			'playlist_id' : id of playlist
		@return dict { 'success' : True }
		"""
		if('site' not in params):
			self.error = 'site is required'
			return False
		return self.request(route = 'api/client/videoclip/assignplaylist', params = params)

	def videoclip_remove_playlist(self, params = {}):
		"""
		remove a videoclip from a playlist

		@params dict params
			'id' : id of videoclip
			'playlist_id' : id of playlist
		@return dict { 'success' : True }
		"""
		if('site' not in params):
			self.error = 'site is required'
			return False
		return self.request(route = 'api/client/videoclip/removeplaylist', params = params)

	def videoclip_poster(self, params = {}, file_path = '', filename = ''):
		"""
		uploads an image file as the poster for a videoclip.

		@params
			dict params
				'id' : id of videoclip
			string file_path
				if supplied, this file is uploaded to the server and attached
				to the videoclip as an image
			string filename
				if supplied & file_path is also given, the uploaded file's
				name is reported to Volar as this filename.  used for easing
				file upload passthrus.  if not supplied, the filename from
				file_path is used.
		@return dict
			{
				'success' : True or False depending on success
				if 'success' == False:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		if file_path == '':
			return self.request(route = 'api/client/videoclip/poster', method = 'GET', params = params)
		else:
			if filename != '':
				post = {'files' : { 'api_poster': (filename, open(file_path, 'rb'))}}
			else:
				post = {'files' : { 'api_poster': open(file_path, 'rb')}}
			return self.request(route = 'api/client/videoclip/poster', method = 'POST', params = params, post_body = post)

	def videoclip_archive(self, params = {}, file_path = ''):
		"""
		upload a video file to a videoclip.

		@params
			dict params
				'id' : id of videoclip
				'site' : slug of site that videoclip is attached to.
			string file_path
				if supplied, this file is uploaded to the server and attached
				to the videoclip
		@return dict
			{
				'success' : True or False depending on success
				'clip' : dict describing videoclip that was modified.
				if 'success' == True:
					'fileinfo' : dict containing information about the
					uploaded file (if there was a file uploaded)
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		if file_path == '':
			return self.request(route = 'api/client/videoclip/archive', method = 'GET', params = params)
		else:
			fileParams = self.upload_file(file_path)
			if fileParams == False:
				return False
			else:
				for key, value in fileParams.iteritems():
					params[key] = value
			return self.request(route = 'api/client/videoclip/archive', method = 'GET', params = params)

	def templates(self, params = {}):
		"""
		gets list of meta-data templates

		@param dict params
			- required -
			'site' : slug of site to filter to.  note that 'sites' is not supported
			- optional -
			'page' : current page of listings.  pages begin at '1'
			'per_page' : number of broadcasts to display per page
			'broadcast_id' : id of broadcast you wish to limit list to.
			'section_id' : id of section you wish to limit list to.
			'id' : id of template - useful if you only want to get details
				of a single template
			'title' : title of template.  useful for searches, as this accepts
				incomplete titles and returns all matches.
			'sort_by' : data field to use to sort.  allowed fields are id, title,
				description, date_modified. defaults to title
			'sort_dir' : direction of sort.  allowed values are 'asc' (ascending) and
				'desc' (descending). defaults to asc
		@return false on failure, dict on success.  if failed, Volar.error can
			be used to get last error string
		"""

		if(('site' not in params)):
			self.error = '"site" parameter is required'
			return False

		return self.request(route = 'api/client/template', params = params)

	def template_create(self, params = {}):
		"""
		create a new meta-data template

		@param dict params
			- required -
			'site' : slug of site to filter to.  note that 'sites' is not supported
			'title' : title of the broadcast
			'data' : list of data fields (dictionaries) assigned to template.
				should be in format:
					[
						{
							"title" : (string) "field title",
							"type" : (string) "type of field",
							"options" : {...} or [...]	//only include if type supports
						},
						...
					]
				supported types are:
					'single-line' - single line of text
					'multi-line' - multiple-lines of text, option 'rows' (not
						required) is number of lines html should display as.
						ex: "options": {'rows': 4}
					'checkbox' - togglable field.  value will be the title of
						the field.  no options.
					'checkbox-list' - list of togglable fields.  values should
						be included in 'options' list.
						ex: "options" : ["option 1", "option 2", ...]
					'radio' - list of selectable fields, although only 1 can be
						selected at at time.  values should be included in
						'options' list.
						ex: "options" : ["option 1", "option 2", ...]
					'dropdown' - same as radio, but displayed as a dropdown.
						values should be included in 'options' array.
						ex: "options" : ["option 1", "option 2", ...]
					'country' - dropdown containing country names.  if you wish
						to specify default value, include "default_select".  this
						should not be passed as an option, but as a seperate value
						attached to the field, and accepts 2-character country
						abbreviation.
					'state' - dropdown containing united states state names.  if
						you wish to specify default value, include "default_select".
						this should not be passed as an option, but as a seperate
						value attached to the field, and accepts 2-character state
						abbreviation.
			- optional -
			'description' : text used to describe the template.
			'section_id' : id of section to assign broadcast to. will default to 'General'.
		@return dict
			{
				'success' : True or False depending on success
				...
				if 'success' == True:
					'template' : dict containing template information,
						including id of new template
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/template/create', method = 'POST', params = { 'site' : site }, post_body = params)

	def template_update(self, params = {}):
		"""
		create a new meta-data template

		@param dict params
			- required -
			'site' : slug of site to filter to.  note that 'sites' is not supported
			'id' : numeric id of template that you are intending to update.
			- optional -
			'title' : title of the broadcast
			'data' : list of data fields assigned to template.  see template_create() for format
			'description' : text used to describe the template.
			'section_id' : id of section to assign broadcast to. will default to 'General'.
		@return dict
			{
				'success' : True or False depending on success
				...
				if 'success' == True:
					'template' : dict containing template information,
						including id of new template
				else:
					'errors' : list of errors to give reason(s) for failure
			}
			Note that if you do not have direct access to update a template (it may be domain or
				client level), a new template will be created and returned to you that does have
				the permissions set for you to modify.  keep this in mind when updating templates.
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/template/update', method = 'POST', params = { 'site' : site }, post_body = params)

	def template_delete(self, params = {}):
		"""
		delete a meta-data template

		the only parameter (aside from 'site') that this function takes is 'id'
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False
		params = json.dumps(params)
		return self.request(route = 'api/client/template/delete', method = 'POST', params = { 'site' : site }, post_body = params)


	def sections(self, params = {}):
		"""
		gets list of sections

		@param dict params
			- required -
			'site' OR 'sites'	slug of site to filter to.
				if passing 'sites', users can include a comma-delimited list of
				sites.  results will reflect all sections in the listed sites.
			- optional -
			'page' : current page of listings.  pages begin at '1'
			'per_page' : number of broadcasts to display per page
			'broadcast_id' : id of broadcast you wish to limit list to.
				will always return 1
			'video_id' : id of video you wish to limit list to.  will always
				return 1.  note this is not fully supported yet.
			'id' : id of section - useful if you only want to get details of
				a single section
			'title' : title of section.  useful for searches, as this accepts
				incomplete titles and returns all matches.
			'sort_by' : data field to use to sort.  allowed fields are id,
				title
			'sort_dir' : direction of sort.  allowed values are 'asc'
				(ascending) and 'desc' (descending)
		@return false on failure, dict on success.  if failed, Volar.error can
			be used to get last error string
		"""

		if(('site' not in params) and ('sites' not in params)):
			self.error = '"site" or "sites" parameter is required'
			return False

		return self.request(route = 'api/client/section', params = params)

	def playlists(self, params = {}):
		"""
		gets list of playlists

		@param dict params
			- required -
			'site' OR 'sites'	slug of site to filter to.
				if passing 'sites', users can include a comma-delimited list of
				sites.  results will reflect all playlists in the listed
				sites.
			- optional -
			'page' : current page of listings.  pages begin at '1'
			'per_page' : number of broadcasts to display per page
			'broadcast_id' : id of broadcast you wish to limit list to.
			'video_id' : id of video you wish to limit list to.  note this is
				not fully supported yet.
			'section_id' : id of section you wish to limit list to
			'id' : id of playlist - useful if you only want to get details of
				a single playlist
			'title' : title of playlist.  useful for searches, as this accepts
				incomplete titles and returns all matches.
			'sort_by' : data field to use to sort.  allowed fields are id,
				title
			'sort_dir' : direction of sort.  allowed values are 'asc'
				(ascending) and 'desc' (descending)
		@return false on failure, dict on success.  if failed, Volar.error can
			be used to get last error string
		"""

		if(('site' not in params) and ('sites' not in params)):
			self.error = '"site" or "sites" parameter is required'
			return False

		return self.request(route = 'api/client/playlist', params = params)


	def playlist_create(self, params = {}):
		"""
		create a new playlist

		@param dict params
			- required -
			'title' : title of the new playlist
			- optional -
			'description' : HTML formatted description of the playlist.
			'available' : flag whether or not the playlist is available
				for public viewing.  accepts 'yes','available','active',
				& '1' (to flag availability) and 'no','unavailable',
				'inactive', & '0' (to flag non-availability)
			'section_id' : id of the section that this playlist should
				be assigned.  the Volar.sections() call can give you a
				list of available sections.  Defaults to a 'General' section
		@return dict
			{
				'success' : True or False depending on success
				...
				if 'success' == True:
					'playlist' : dict containing playlist information,
						including id of new playlist
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/playlist/create', method = 'POST', params = { 'site' : site }, post_body = params)

	def playlist_update(self, params = {}):
		"""
		update existing playlist

		@param dict params
			- required -
			'id' : id of playlist you wish to update
			- optional -
			'title' : title of the new playlist.  if supplied, CANNOT be
				blank
			'description' : HTML formatted description of the playlist.
			'available' : flag whether or not the playlist is available
				for public viewing.  accepts 'yes','available','active',
				& '1' (to flag availability) and 'no','unavailable',
				'inactive', & '0' (to flag non-availability)
			'section_id' : id of the section that this playlist should
				be assigned.  the Volar.sections() call can give you a
				list of available sections.  Defaults to a 'General' section
		@return dict
			{
				'success' : True or False depending on success
				if 'success' == True:
					'playlist' : dict containing playlist information,
						including id of new playlist
				else:
					'errors' : list of errors to give reason(s) for failure
			}
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False

		params = json.dumps(params)
		return self.request(route = 'api/client/playlist/update', method = 'POST', params = { 'site' : site }, post_body = params)

	def playlist_delete(self, params = {}):
		"""
		delete a playlist

		the only parameter (aside from 'site') that this function takes is 'id'
		"""
		site = params.pop('site', None)
		if site == None:
			self.error = 'site is required'
			return False
		params = json.dumps(params)
		return self.request(route = 'api/client/playlist/delete', method = 'POST', params = { 'site' : site }, post_body = params)


	def upload_file(self, file_path):

		filePathBaseName = os.path.basename(file_path)
		handshakeRes = self.request('api/client/broadcast/s3handshake', method = 'GET', params = { 'filename' : filePathBaseName });
		if not handshakeRes:
			if self.error == '':
				self.error = "Could not initiate file upload"
			return False
		returnVals = {
			'tmp_file_id': handshakeRes['id'],
			'tmp_file_name': handshakeRes['key']
		}
		dispositionFileName = filePathBaseName.replace('"', '')

		try:
			connection = S3Connection(aws_access_key_id=handshakeRes['access_key'], aws_secret_access_key=handshakeRes['secret'], security_token=handshakeRes['token'])
		except Exception as e:
			self.error = "Connection failed: {0}".format(e)
			return False

		try:
			bucket = S3Bucket(connection = connection, name = handshakeRes['bucket'])
			k = S3Key(bucket = bucket, name = handshakeRes['key'])
			k.content_disposition = 'attachment; filename="{0}"'.format(dispositionFileName)
			returnVals['bytes_uploaded'] = k.set_contents_from_filename(file_path, policy = 'public-read')
		except Exception, e:
			self.error = "{0}".format(e)
			return False

		return returnVals


	def request(self, route, method = '', params = {}, post_body = None):
		if method == '':
			method = 'GET'

		params_transformed = {}
		for key, value in sorted(params.iteritems()):
			if isinstance(value, dict):
				for v_key, v_value in sorted(value.iteritems()):
					params_transformed[ key + '[' + self.convert_val_to_str(v_key) + ']' ] = v_value
			elif isinstance(value, list) or isinstance(value, tuple):
				for v_key, v_value in enumerate(value):
					params_transformed[ key + '[' + self.convert_val_to_str(v_key) + ']' ] = v_value
			else:
				params_transformed[key] = value

		params_transformed['api_key'] = self.api_key
		signature = self.build_signature(route, method, params_transformed, post_body)
		params_transformed['signature'] = signature

		url = '/' + route.strip('/')

		if self.secure:
			url = 'https://' + self.base_url + url
		else:
			url = 'http://' + self.base_url + url

		try:
			if method == 'GET':
				r = requests.get(url, params = params_transformed)
			else:
				data = {}
				files = None
				# see if there's file data
				if post_body is not None:
					if type(post_body) is str:
						data = post_body
					elif type(post_body) is dict:
						for i in post_body:
							if i == 'files':
								files = post_body[i]	#files are sent multipart
							else:
								data[i] = post_body[i]

				if data == {}:	#no data
					data = None

				r = requests.post(url, params = params_transformed, data = data, files = files)
			return json.loads(r.text)
		except Exception as e:
			self.error = "Request failed with following error: " + e.message
			return False

	def build_signature(self, route, method = '', get_params = {}, post_body = None):
		if method == '':
			method = 'GET'

		signature = str(self.secret) + method.upper() + route.strip('/')

		for key, value in sorted(get_params.iteritems()):
			if isinstance(value, dict):
				for v_key, v_value in sorted(value.iteritems()):
					signature += key + '[' + self.convert_val_to_str(v_key) + ']=' + self.convert_val_to_str(v_value)
			elif isinstance(value, list) or isinstance(value, tuple):
				v_key = 0
				for v_value in value:
					signature += key + '[' + self.convert_val_to_str(v_key) + ']=' + self.convert_val_to_str(v_value)
					v_key = v_key + 1
			else:
				signature += key + '=' + self.convert_val_to_str(value)

		signature = signature.encode('ascii')
		if type(post_body) is str:
			signature += post_body

		signature = base64.b64encode(hashlib.sha256(signature).digest())[0:43]
		signature = signature.rstrip('=')
		return signature

	def convert_val_to_str(self, val):
		if isinstance(val, bool):
			if val:
				return '1'
			else:
				return '0'
		else:
			return str(val)