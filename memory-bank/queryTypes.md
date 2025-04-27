# Common Query Types for Yojna Khojna

This document outlines the various categories of queries that users typically make to the Yojna Khojna system. Understanding these query patterns helps in designing better entity extraction and retrieval strategies.

## Social Welfare Schemes

* "प्रधानमंत्री आवास योजना के लिए कौन पात्र है?" (Who is eligible for PM Housing Scheme?)
* "मुफ्त गैस कनेक्शन कैसे मिलेगा?" (How to get free gas connection?)
* "मुझे सरकारी योजनाओं के बारे में बताएं" (Tell me about government schemes)
* "क्या मुझे पीएम किसान के पैसे मिलेंगे?" (Will I get PM Kisan money?)

## Healthcare Benefits

* "आयुष्मान भारत के तहत कौन सा इलाज मिलता है?" (What treatments are covered under Ayushman Bharat?)
* "जननी सुरक्षा योजना में कितना पैसा मिलता है?" (How much money is given in Janani Suraksha Yojana?)
* "स्वास्थ्य बीमा के लिए कैसे अप्लाई करें?" (How to apply for health insurance?)
* "मेरे गांव में आयुष्मान कार्ड कहां बनेगा?" (Where will Ayushman card be made in my village?)

## Agricultural Support

* "किसान क्रेडिट कार्ड के लिए क्या दस्तावेज चाहिए?" (What documents are needed for Kisan Credit Card?)
* "फसल बीमा के लिए कैसे आवेदन करें?" (How to apply for crop insurance?)
* "सिंचाई के लिए सब्सिडी कितनी मिलती है?" (How much subsidy is available for irrigation?)
* "ट्रैक्टर खरीदने पर कितनी छूट मिलेगी?" (How much discount will I get for buying a tractor?)

## Education Support

* "छात्रवृत्ति के लिए आवेदन कैसे करें?" (How to apply for scholarship?)
* "मिड-डे मील योजना में क्या मिलता है?" (What is provided in Mid-Day Meal scheme?)
* "लड़कियों के लिए शिक्षा योजनाएं क्या हैं?" (What are education schemes for girls?)
* "स्कूल यूनिफॉर्म के लिए क्या कोई योजना है?" (Is there any scheme for school uniforms?)

## Employment Programs

* "मनरेगा में कितने दिन काम मिलता है?" (How many days of work is provided in MGNREGA?)
* "स्किल इंडिया में ट्रेनिंग कैसे ले?" (How to get training in Skill India?)
* "मुद्रा लोन कैसे मिलेगा?" (How to get Mudra loan?)
* "स्टार्टअप के लिए सरकारी सहायता कैसे मिलेगी?" (How to get government support for startups?)

## Utility Subsidies

* "मुफ्त बिजली योजना के लिए कौन पात्र है?" (Who is eligible for free electricity scheme?)
* "पानी की सब्सिडी कैसे मिलेगी?" (How to get water subsidy?)
* "सोलर पैनल पर कितनी सब्सिडी मिलती है?" (How much subsidy is available for solar panels?)
* "एलपीजी सिलेंडर पर कितना डिस्काउंट है?" (How much discount is there on LPG cylinders?)

## Disaster Relief

* "बाढ़ में घर नष्ट होने पर क्या मदद मिलेगी?" (What help will I get if my house is destroyed in flood?)
* "फसल बर्बाद होने पर कितना मुआवजा मिलेगा?" (How much compensation for crop damage?)
* "बिजली गिरने से नुकसान का मुआवजा कितना है?" (How much compensation for lightning strike damage?)
* "सूखे के दौरान किसानों को क्या सहायता मिलती है?" (What assistance do farmers get during drought?)

## Special Category Benefits

* "विधवा पेंशन के लिए क्या करना होगा?" (What to do for widow pension?)
* "दिव्यांग पेंशन कितनी मिलती है?" (How much is the disability pension?)
* "वरिष्ठ नागरिक योजनाओं के बारे में बताएं" (Tell me about senior citizen schemes)
* "एससी/एसटी छात्रों के लिए क्या स्कॉलरशिप हैं?" (What scholarships are available for SC/ST students?)

## Entity Types Important for Extraction

Based on these query patterns, the following entity types are critical to extract:

1. **Scheme Names**: प्रधानमंत्री आवास योजना, आयुष्मान भारत, मनरेगा, etc.
2. **Benefit Types**: पेंशन, लोन, सब्सिडी, स्कॉलरशिप, etc.
3. **Beneficiary Categories**: किसान, विधवा, छात्र, दिव्यांग, etc.
4. **Document Types**: आधार कार्ड, राशन कार्ड, आय प्रमाण पत्र, etc.
5. **Processes**: आवेदन, अप्लाई, रजिस्ट्रेशन, etc.
6. **Monetary Terms**: पैसा, रुपये, सब्सिडी, मुआवजा, etc.
7. **Locations**: गांव, ब्लॉक ऑफिस, पंचायत, etc.
8. **Disaster Types**: बाढ़, सूखा, बिजली गिरना, etc.
9. **Application Places**: ब्लॉक ऑफिस, पंचायत, सीएससी, etc.
10. **Time Periods**: महीना, साल, अवधि, etc. 