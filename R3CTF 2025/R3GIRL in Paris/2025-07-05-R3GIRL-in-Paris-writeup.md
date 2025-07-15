---
layout: post
title:  "R3GIRL in Paris - R3CTF 2025 Write-up"
---
## R3GIRL in Paris - R3CTF Write-up

![Banner](assets/files/r3girl-in-paris/banner.png)

**Challenge:** R3GIRL in Paris
**Category:** Misc, OSINT
**Points:** 200
**Author:** MinousE3

### Introduction
For this challenge, “R3GIRL in Paris,” we were given a single file: [`R3GIRL-in-Paris.png`](/assets/files/r3girl-in-paris/R3GIRL-in-Paris.png). The goal was to determine the original name of the building featured in the image, as well as the first names of the artists responsible for the mural on its side.

The flag format was specified as: 
```bash 
R3CTF{Place-Name-FirstnameN}
```

We were instructed to preserve the original casing of the building’s name, replace spaces with hyphens, and include the first names of the mural’s creators without any accents. The artists’ names were to be listed in the order they appeared or were best known for the mural.

### Analyzing the [`R3GIRL-in-Paris.png`](/assets/files/r3girl-in-paris/R3GIRL-in-Paris.png) File
Now, let’s examine [`R3GIRL-in-Paris.png`](/assets/files/r3girl-in-paris/R3GIRL-in-Paris.png):

![R3GIRL-in-Paris](/assets/files/r3girl-in-paris/R3GIRL-in-Paris.png)

The image depicted a tall building in what appeared to be a residential neighborhood, with a massive and highly detailed mural covering the side wall. The artwork was surreal, blending animals, mythological creatures, and human forms. This, combined with the scale and complexity of the piece, suggested that it was not random graffiti but part of an organized public art initiative.

Manual investigation and OSINT (Open-Source Intelligence) techniques were clearly necessary. Reverse image search, architectural cues, mural databases, and city-specific public art programs were all potential avenues. The image itself would be the key to unlocking the required information.

### Method
The R3GIRL in Paris challenge revolved around visual identification through open-source intelligence techniques. Since the only asset provided was an image [`R3GIRL-in-Paris.png`](/assets/files/r3girl-in-paris/R3GIRL-in-Paris.png), a reverse image approach was the logical first step.

To begin the investigation, I used Google Lens to perform a reverse image search. While the original image was relatively zoomed in, Lens helped return similar images taken from a wider angle. One of those hits showed the same building but with a visible banner on the lower facade, reading “Notre-Dame de Chine.”

![Method 1](/assets/files/r3girl-in-paris/method-1.png)

This was a crucial breakthrough. The visible text hinted that the location could be a church. A quick search on Google Maps confirmed that this building is known as Église Notre-Dame de Chine, a Roman Catholic church located in the 13th arrondissement of Paris. The structure and surrounding architecture matched the original image, verifying the location.

![Method 2](/assets/files/r3girl-in-paris/method-2.png)

Next, I attempted to identify the artist(s) behind the mural. I initially tried to search using keywords like ```Notre Dame de Chine``` and ```Église Notre-Dame de Chine```

Unfortunately, none of the official public art databases or news sites listed the artist’s name directly.

That’s when I noticed a new lead in one of the wide-angle image search results: a phrase printed on the building wall — "De tous pays viendront tes enfants" (English: “From all countries your children will come”). Recognizing this as a potential title of the mural or fresco, I searched for it directly.

![Method 3](/assets/files/r3girl-in-paris/method-3.png)

This led me to a TripAdvisor entry titled Fresque “De tous pays viendront tes enfants”, which detailed the mural’s background. In a user-submitted review, I found a valuable description stating that the artwork was created in 1988 and painted by Cyril Vachez and David N. This matched the visual style and date, confirming the artist identities.

![Method 4](/assets/files/r3girl-in-paris/method-4.png)

![Method 5](/assets/files/r3girl-in-paris/method-5.png)

After identifying the correct location as Église Notre-Dame de Chine and confirming the artists’ names as Cyril Vachez and David N, the final step was to format the flag according to the specification:
1. The place name becomes ```Eglise-Notre-Dame-de-Chine``` (original casing, accents removed, hyphens instead of spaces)
2. The artist first names are ```Cyril``` and ```David``` (no surnames, only first names in the order found)

Thus, the final flag is:
```bash
R3CTF{Eglise-Notre-Dame-de-Chine-Cyril-David}
```
![Method 6](/assets/files/r3girl-in-paris/method-6.png)
