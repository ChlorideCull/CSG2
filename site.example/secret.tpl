<div class="contentbox">
	<h2>Information from Python Integration</h2>
	<p>
% import platform, sys
		We are running on <b>{{platform.python_implementation()}} {{platform.python_version()}} ({{platform.architecture()[0]}})</b>.
		It was built on <b>{{sys.platform}}</b>.
		The host OS identifies as <b>{{platform.platform(aliased=True)}}</b>.
	</p>
</div>
