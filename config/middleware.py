# import base64 , os 
# from django.conf import settings 
# from django.utils.deprecation import MiddlewareMixin 

# class CSPNonceMiddleware(MiddlewareMixin):   
#     def process_request(self, request):
#          # تولید nonce برای هر درخواست   
#          request.nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
#     def process_response(self, request, response):    
#         # تزریق nonce به هدر CSP
#         if hasattr(request, 'nonce') and 'Content-Security-Policy' in response.headers:  
#         csp = response.headers['Content-Security-Policy']      
#         csp = csp.replace("'nonce-{{ nonce_value }}'", f"'nonce-{request.nonce}'")   
#         response.headers['Content-Security-Policy'] = csp  
#         # اضافه کردن nonce به context برای استفاده تو قالب‌ها  
#         if hasattr(response, 'context_data'):     
#             response.context_data['nonce_value'] = request.nonce       
#         return response
