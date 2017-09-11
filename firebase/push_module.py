from firebase.models import MyDevice

def push_fcm_specific_divce(request):
    token = 0

    MyDevice = get_device_model()    
    
    device = MyDevice.objects.get(reg_id = token) 

    device.send_message({"message":'push message'})

def push_fcm_multicast(request):
    MyDevice = get_device_model()
  
    device = MyDevice.objectys.all()

    device.send_message({'message':'push message'})  
    	   
