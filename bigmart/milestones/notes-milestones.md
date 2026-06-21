Project 2

The BigMart Sales project focuses on analyzing retail data to understand the key factors influencing product sales across multiple outlets and to develop predictive and analytical insights. The dataset consists of product-level and outlet-level attributes such as item price (MRP), visibility, category, outlet type, and sales.This calls for brushing up my EDA skills and also makes me think deeper on various features and imputations.



I have divided this project into two parts. The first part is to accurately predict item outlet sales and understand the main drivers of revenue.



The second part is to come up with a standalone anomaly detection and business insight module using the PyOD library. Rather than treating outliers as noise to be removed, I want to group anomalies into interpretable categories such as:

A. High Price, Low Sales

Indicators of pricing inefficiency



B. Low Visibility, High Sales

Hidden high-demand products

Opportunity for promotion



Together, these notebooks provide a dual perspective: one focused on prediction and the other on discovery. This combined approach enables not only accurate forecasting but also actionable business insights, making the project more aligned with real-world decision-support systems rather than purely academic modeling.


----
The way you split this into prediction and anomaly detection is something I haven't really seen done together in a lot of projects we've covered, and it makes a lot of sense once you think about it. Most of what I've read tends to treat outlier removal as just a preprocessing step you get out of the way before modeling, so reframing anomalies as actually useful signals for business insights is a perspective shift that clicked for me reading your post. The category breakdowns you laid out, like high price with low sales versus low visibility with high sales, remind me of how we discussed feature relationships in class where the combination of two variables tells you something neither one does alone.



What I keep coming back to though is how the Data Preparation phase you mentioned, especially the imputation piece, is going to carry a lot of weight for both parts of your project, not just the predictive model. If you impute item visibility or MRP in a way that smooths over the actual quirks in the data, you might accidentally clean away the exact patterns that your PyOD module is supposed to catch. That tension between making the data clean enough to model and keeping it messy enough to surface real anomalies seems like the core challenge here, and it is something I am genuinely still trying to wrap my head around in terms of best practices. It makes me wonder how you are planning to handle that boundary between what gets cleaned in Part 1 versus what stays raw or minimally transformed for Part 2, because those two goals could pull in opposite directions depending on your choices early in the pipeline.


---
I think your project takes an interesting approach by combining predictive modeling with anomaly detection. Many retail analytics projects focus solely on forecasting sales, but your second component adds significant business value by identifying unusual patterns that may lead to actionable insights. The idea of treating anomalies as opportunities for discovery rather than simply removing them from the dataset reflects how analytics is often applied in real-world business environments.



Your focus on exploratory data analysis (EDA) is also important. The BigMart dataset contains several features that can influence sales, including item visibility, outlet characteristics, and product categories. Thorough EDA can help uncover relationships, identify missing values, and guide feature engineering decisions that improve model performance. As Han et al. (2022) note, understanding the data before model development is a critical step in the data mining process and often contributes significantly to overall project success.



I particularly like your anomaly categories. For example, products with high prices and low sales may indicate pricing issues, while products with low visibility and high sales could reveal hidden demand that deserves additional marketing support. You might also consider examining categories such as high visibility but low sales, which could indicate ineffective promotions, or unusually strong sales in specific outlet types that may reveal location-based opportunities.



Using PyOD is a strong choice because it provides access to multiple anomaly detection algorithms, allowing you to compare approaches and evaluate which method best identifies meaningful business patterns. Combining predictive analytics with anomaly detection creates a more comprehensive decision-support framework by addressing both forecasting and business optimization objectives.



Overall, your project demonstrates a strong balance between technical modeling and practical business application. I look forward to seeing how the anomaly detection component complements your sales prediction results and contributes to actionable retail insights.
