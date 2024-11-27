from gcp_adc_util.inspect import ADCInspect


p = ADCInspect(debug=False)

print(p.getProjectID())
print(p.getPrincipal())