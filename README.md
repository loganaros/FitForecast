# Fit Forecast

This app takes in input from a user, and uses a weather API and the OpenAI API to generate a contextually accurate outfit recommendation based on your current location, weather conditions and style that the user is looking for.
To use the app, you input your location, vibe that you are going for, and whether you would like it to be more masculine or feminine. The weather API can handle input such as cities, countries, or if left blank will grab your current location based on your IP address.
Once you submit the form, the data will be sent to the OpenAI API after gathering the weather information and filling out some hardcoded prompt engineering on the backend, and will return an outfit recommendation which will then send another request to generate an image of the outfit based on the response from OpenAI.

PLEASE MINIMIZE REQUESTS AS IT COSTS MONEY AND ONLY HAS A SMALL LIMIT ATTACHED TO IT FOR DEMONSTRATION

Deployed at: https://capstone1deployable.onrender.com/
