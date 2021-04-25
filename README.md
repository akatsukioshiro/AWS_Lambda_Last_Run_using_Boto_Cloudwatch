# AWS_Lambda_Last_Run_using_Boto_Cloudwatch
Get the Last Run Timestamp of an AWS Lambda Function - Usage: To find unused Lambda Functions

Idea: Well, this helps to find the unused Lambda Functions. How ? - By getting the last runtime of a Lambda Function from CloudWatch Logs.

# Method 1 - example_Method_1.py
* This does the Job eventually but is too slow, unresponsive sometimes.
* Might run after a few 5-10 tries, sometimes earlier sometimes whenever it wants.
* Yes, since the results array is empty, when no logs read, it throws error which I decided not to handle for now.

# Method 2 - example_Method_2.py
* This also has a delay, but is way more faster and efficient compared to previous method.
* This will defenitely yield result in 1-3 tries.
