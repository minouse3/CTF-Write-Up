## Friday 14 - Haunted Pumpkin CTF '25 Write-up

![Banner](assets/banner.png)

**Challenge:** Friday 14
**Category:** OSINT
**Points:** 100
**Author:** minouse3

### Introduction
This challenge is a continuation of the Friday 13 challenge. After searching for his phone number, now they want us to find his email that related to his role.

The flag should be in the format:
```
hpCTF{<email>}
```

### How to find his email?
If you googling "Ari Lehman" a little bit, you can find his Website, [firstjason.com](https://firstjason.com), which related to his role as child Jason Voorhees in the film Friday the 13th.

![method-1](assets/method-1.png)

Then, you can scroll down the website, and you will find his Youtube Channel, FIRST JASON.

![method-2](assets/method-2.png)

After that, you can open his Channel informations by clicking more and you will see his email that related to his role as child Jason Voorhees, firstjason13@gmail.com.

### Flag
```
hpCTF{firstjason13@gmail.com}
```