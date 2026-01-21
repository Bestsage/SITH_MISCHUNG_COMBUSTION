
print("Debugging RocketCEA attributes:")
try:
    from rocketcea.cea_obj import CEA_Obj
    print([m for m in dir(CEA_Obj) if "get" in m])
except Exception as e:
    print(e)
