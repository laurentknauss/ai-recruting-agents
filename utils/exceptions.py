
class ResumeProcessingError(Exception): 
  """Base exception for resume processing errors""" 
  
  pass 



class ExtractionError(ResumeProcessingError): 
  """Raised when resume extraction fails""" 
  
  pass 



class AnalyticsError(ResumeProcessingError): 
  """Raised when resume analysis fails""" 
  
  pass 



class MatchingError(ResumeProcessingError): 
  """Raised when job  matching fails""" 
  
  pass 


class ScreeningError(ResumeProcessingError): 
  """raised when candidate screening fails""" 
  
  pass 

class RecommendationsError(ResumeProcessingError): 
  """Raised when generating recommendations fails"""
  
  pass 




