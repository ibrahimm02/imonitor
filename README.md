# iMonitor

![Overview Page](https://github.com/ibrahimm02/imonitor/blob/master/static/images/Overview-page.png?raw=true)

A cloud monitoring service that integrates with Amazon Web Services (AWS) and provides the users with data insights, metrics, and graphs for various cloud services.

## Installation

To run this application, follow these steps:

1. Clone the repository:

```sh
git clone https://github.com/ibrahimm02/imonitor.git
cd imonitor
```

2. Create a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a .env file with the following contents:

```sh
export AWS_SERVER_ACCESS_KEY="KEY"
export AWS_SERVER_SECRET_KEY="KEY"
export REGION_NAME="REGION"
```
Replace "KEY" with your AWS server access key and secret key, and replace "REGION" with the region of your AWS server.

4. Build the Docker image:

```sh
docker build --tag imonitor .
```

5. Run the Docker container:

```sh
docker run -d -p 5000:5000 imonitor
```

The application should now be running and can be accessed at http://localhost:5000.

## Contributing

Contributions are always welcome! If you find any issues or want to add new features, feel free to submit a pull request.

## License

This project is licensed under the MIT License. For more information, see the LICENSE file.