.. Nestmatics entries format file to hold information about the entries format in the database.


.. _my-reference-label:

Database Documents Format
==============================================

In this section, the format for the documents inside each collection in the database will be
explained and defined for easier access when making CRUD requests to the database through the API.


Order To Insert Into Database
-----------------------------------------------

When using the API, and/or there is need to insert documents (entries) for the first time, the recommended
order to insert entries is the following:

1. Users
2. Service Area
3. Nests
4. Nest Configuration
5. Drop Strategies
6. Experiments
7. Rides

This order is recommended due to the fact that the lower items on the list rely on the upper items on the list.
For example, a Nest needs an id of a valid service area that is already inserted on the system
to complete all the fields necessary for the nest insertion into the database.

Users Collection
-----------------------------------------------

The Users Collection holds information about Users registered in the system. The documents in this
collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "email": email of user. This email will act as an identifier for the authentication
                process and the overall system,
        "type": type of the user in the system. This field dictates user permissions, therefore, allowed
                    values for this field is "user" or "admin"
    }

Service Area Collection
-----------------------------------------------

The Service Area Collection holds information such as coordinates and the service area name of service areas
in the system. The documents in this collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "area_name": Name of the Service Area. Must be a string with at least one character,
        "coords": {
                    "coordinates": 2D array containing lat and lon coordinates the comprises the
                                   service area polygon,
                    "type": (optional) type of the polygon in case the service area should be used in
                            KML format
                  }
    }

Nests Collection
-----------------------------------------------

The Nests Collection holds information such as coordinates and the name of Nests
in the system. The documents in this collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "user": id (document id) of the user who created the Nest,
        "service_area": id (document id) of the service area this Nest belongs to,
        "nest_radius": radius of nest. Radius will dictate area that Nest encompasses,
        "nest_name": name of the nest. Must be a string and contain at least one character,
        "coords": {
                    "lat": coordinate latitude of the Nest
                    "lon": coordinate longitude of the Nest
                  }
    }

Nests Configuration Collection
-----------------------------------------------

The Nests Configuration Collection holds information about Nest Configurations such as nest id (nest that the
configuration belongs to) and vehicle quantity deployed on the nest for the specified day. The documents in this
collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "nest": id (document id) of the Nest this configuration belongs to,
        "start_date": date that nest configuration started (ISO 8601 format),
        "end_date": date that the nest configuration ended (ISO 8601 format),
        "vehicle_qty": Quantity of vehicles deployed on that Nest for specified
                        start and end dates
    }


Drop Strategy Collection
-----------------------------------------------

The Drop Strategy Collection in the database will have documents of the format:

.. code-block:: json

    {
        "_id": id of document,
        "start_date": date when drop strategy started (ISO 8601 format),
        "end_date": date when drop strategy ended (ISO 8601 format),
        "service_area": id of service area the drop strategy was implemented in,
        "days": array containing json objects for each day the drop strategy was implemented.
    }

The Days field in the drop strategy will have the following format:

.. code-block:: json

    {
        "date":(optional) date of the day being described (ISO 8601 format),
        "configurations": array of configuration ids for the nest configurations deployed that day
    }

Experiments Collection
-----------------------------------------------

The Experiments Collection holds information about Experiments such as the ids of the configurations to compare
and an experiment name. The documents in this collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "nest": id (document id) of the Nest this experiment belongs to,
        "name": name of the experiment,
        "config1": Nest configuration ID of 1 configuration to compare,
        "config2": Nest configuration ID of 2 configuration to compare,
        "date": date that the experiment was created (ISO 8601 format)
    }


Rides Collection
-----------------------------------------------

The Rides Collection holds information about Rides such as the time a ride started and ended, the coordinates of
where the ride started and ended, the service area where it took place, etc. The documents in this collection will
have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "date": date that the ride took place (ISO 8601 format),
        "bird_id": id (from bird) of the vehicle that performed this ride,
        "start_time": time stamp of when the ride started (ISO 8601 format),
        "end_time": time stamp of when the ride ended (ISO 8601 format),
        "service_area": {
                            "_id": id of service area where this ride happened
                        },
        "ride_cost": cost of the ride,
        "coords": {
                    "start_lat": latitude of ride's start location,
                    "start_lon": longitude of ride's start location,
                    "end_lat": latitude of ride's end location,
                    "end_lon": longitude of ride's end location
                  }
    }

Models Collection
-----------------------------------------------

The Models collection will hold information about the Machine Learning models used to create predictions.
The documents in this collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "critical_val_error": critical validation error of the model,
        "validation_error": validation Error of the model,
        "training_error": training error of the model,
        "service_area": id of service area this model was created for,
        "creation_date": date in which this model was created (ISO 8601 format),
        "model_file": path of model files
    }

Predictions Collection
-----------------------------------------------

The Models collection will hold information about the Machine Learning models used to create predictions.
The documents in this collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "model_id": id of model that this prediction was made with,
        "service_area": id of service area for this prediction,
        "prediction_date": date of day that is being predicted (ISO 8601 format),
        "creation_date": date of when the prediction was created (ISO 8601 format),
        "error_metric": error metric resulting from the comparison of the prediction output and the real output
                        for the specified day,
        "prediction": 3D array holding the prediction data
        "features": dictionary holding information of each feature's impact on the prediction
    }

The features field holds numerical information of the impact a specific feature had on the prediction. The higher
the number, the higher the impact of the feature on the prediction. This field will have the format:

.. code-block:: json

    {
        "weather": {
            "precipitation": precipitation relevance on prediction value,
            "temperature": precipitation relevance on prediction value
        },
        "rides": rides relevance on prediction value,
        "buildings": buildings relevance on prediction value,
        "streets": streets relevance on prediction value,
        "amenities": amenities relevance on prediction value
    }

Other Collections
-----------------------------------------------

Other collections in the system.


Weather
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The weather collection holds weather information (precipitation and temperature) of a specific day on a service area.
Documents in this collection will have the following format:

.. code-block:: json

    {
        "_id": id of document,
        "precipitation": precipitation of the area for the specified day,
        "temperature": temperature of the area for the specified day,
        "service_area": id of service area for this weather information,
        "timestamp": time stamp of this weather information (ISO 8601 format)
    }

Buildings/Streets/Amenities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Buildings, Street, and Amenities collection holds the buildings, street or amenities bitmap path, respectively,
of a particular service area. These three collection share a common structure. Documents in these collections will
have the format:

.. code-block:: json

    {
        "_id": id of document,
        "bitmap_file": file path to the buildings/streets/amenities bitmap file,
        "service_area": id of service area for this information,
        "timestamp": time stamp of when this information was inserted into the system (ISO 8601 format)
    }
