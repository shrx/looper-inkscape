# Looper for Inkscape v1.0.0

Looper is an Inkscape extension that helps automate duplication of groups and objects. One can control properties like Rotate, Scale and Opacity while duplicating. This powerful combination enables artists and designers to create interesting geometric and organic patterns.

This is an unofficial Inkscape port of the [Looper Sketch plugin](https://github.com/sureskumar/Looper) by Sures Kumar.

## Installation

Make sure you have Inkscape 1.1 or newer installed.

1. [Download the ZIP file of the latest release](https://github.com/shrx/looper-inkscape/releases)
2. Unzip `looper.inx` and `looper.py` into your Inkscape user extensions directory (shown in *Edit → Preferences → System → User extensions*)
3. Restart Inkscape. Looper appears under *Extensions → Arrange → Looper…*

## Features

### Duplication count
Duplicate selected group or object by providing the duplication count or Looper can automatically calculate the count based on the rotation angle to form a complete circle.

### Scale
Selected group or object can be scaled by absolute value (px), proportional value (%) or at random. 

### Opacity
Opacity of selected group or object can be set to update at random, increase from 0 to 100 or decrease from 100 to 0.

### Rotate
Rotate selected group or object by providing a specific rotation angle or Looper can automatically calculate the angle required based on the duplication count to form a complete circle.

Rotation angle can be incremented in a linear fashion, randomly or can be set to increment sinusoidally.

### Move
Selected group or object can be moved Horizontally, Vertically and Diagonally with a set increment value. Duplicated items can also be distributed randomly within a given dimension (width & height)

### Form a grid
Duplicate the selected group or object to form a grid. Number of columns, rows, horizontal margin and vertical margin can be manipulated. You can also alter other properties like opacity, rotate and scale to the grid elements.

## Examples
![Looper sample](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_16_exp.jpg)

#### Rotate (linear) 
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_18.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_25.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_10.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_26.jpg)

#### Rotate (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_04.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_03.jpg)

#### Rotate (linear) + Opacity (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_11.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_31.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_13.jpg)

#### Rotate (linear) + Scale (linear)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_22.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_34.jpg)

#### Rotate (linear) + Scale (sinusoidal)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_06.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_05.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_12.jpg)

#### Rotate (random) + Scale (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_19.jpg)

#### Rotate (sinusoidal) + Scale (sinusoidal)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_20.jpg)

#### Rotate (sinusoidal) + Scale (sinusoidal) + Opacity (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_14.jpg)

#### Rotate (sinusoidal) + Scale (linear) + Opacity (Fade to 0)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_16.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_23.jpg)

#### Rotate (linear) + Scale (linear) + Opacity (Fade to 0)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_01.jpg)

#### Rotate (random) + Scale (random) + Opacity (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_29.jpg)

#### Rotate (linear) + Scale (sinusoidal) + Opacity (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_33.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_27.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_32.jpg)

#### Rotate (linear) + Move (horizontal)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_07.jpg)

#### Rotate (linear) + Move (vertical)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_08.jpg)

#### Rotate (linear) + Move (diagonal)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_09.jpg)

#### Rotate (random) + Move (random) + Opacity (random)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_17.jpg)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_24.jpg)

#### Move (vertical) + Opacity (Fade to 0)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_15.jpg)

#### Move (vertical) + Scale (linear) + Opacity (Fade to 0)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_21.jpg)

#### Move (horizontal + vertical)
![Looper example](https://github.com/sureskumar/Looper/raw/master/assets/looper_example_28.jpg)


## Thanks

* [Sures Kumar](https://github.com/sureskumar), author of the original Looper Sketch plugin

## Port notes

See [PORTING.md](PORTING.md) for differences from the Sketch original and development/test instructions.
