{{/*
Return the fully qualified app name.
*/}}
{{- define "opticon-hub.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" $name .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/*
Return the name of the chart
*/}}
{{- define "opticon-hub.name" -}}
{{- .Chart.Name -}}
{{- end -}}