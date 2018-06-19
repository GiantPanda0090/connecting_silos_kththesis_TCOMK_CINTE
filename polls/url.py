# Django page frontend page

from django.conf.urls import url,include


from . import views

urlpatterns = [

url(r'^index_submit$', views.index_submit, name='index_submit'),
url(r'^retrive_session_baseon_id$', views.retrive_session_baseon_id, name='retrive_session_baseon_id'),
url(r'^retrive_generalsession_baseon_id$', views.retrive_generalsession_baseon_id, name='retrive_generalsession_baseon_id'),
url(r'^update_database$', views.update_database, name='update_database'),






url(r'^lti$', views.lti_proporsal, name='lti'),
url(r'^index_submit_thesis$', views.index_submit_thesis, name='index_submit_thesis'),

url(r'^lti_th$', views.lti_thesis, name='lti_th'),
url(r'^generate_polopoly_json$', views.generate_polopoly_json, name='generate_polopoly_json'),


url(r'^lti_bound$', views.tool_config, name='lti_bound'),
url(r'^lti_bound_theis$', views.tool_config_thesis, name='lti_bound_theis'),
url(r'^install$', views.install, name='install'),
url(r'^install_2$', views.install_2, name='install_2'),
url(r'^accept_form$', views.accept_form, name='accept_form'),
url(r'^modsOut', views.modsOut, name='modsOut'),




]
