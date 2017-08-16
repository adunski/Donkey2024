![travis](https://travis-ci.org/wroscoe/donkey.svg?branch=dev)

# donkeycar: a python self driving library 

Donkeycar is minimalist and modular self driving library written in Python. It is 
developed for hobbiests and students with a focus on allowing fast experimentation and easy 
community contributions.  

#### Quick Links
* [Code Documentation](http://docs.donkeycar.com)
* [Instructions to build a Donkey2 car.](http://www.donkeycar.com)

#### Use Donkey if you want to:
* Make an RC car drive its self.
* Compete in self driving races like [DIY Robocars](diyrobocars.com)
* Experiment with different driving methods.
* Add parts and sensors to your car.
* Log sensor data. (images, user inputs, sensor readings) 
* Drive yoru car via a web or game controler.
* Leverage community contributed driving data.
* Use existing hardware CAD designs for upgrades.

### Getting started. 
After building a Donkey2, here are the steps to start driving.

install donkey
```
pip install donkeycar
```

Create a car folder.
```
donkey createcar --path ~/d2
```

Start your car.
```
python ~/d2/manage.py drive
```

Now you can control your car by going to `<ip_address_of_your_pi>:8887/drive`
