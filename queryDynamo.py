import dynamostorage as Dynamo
import keyvalue.stemmer as Stemmer
import sys

def getImages(argv):
    for x in argv:
        response = dynamo_labels.queryItem(Stemmer.stem(x))
        if ('Items' in response):
            items = response['Items']
            for item in items:
                url = dynamo_images.getItem(
                    { 
                        'keyword': item['value'] 
                    })
                print(str(x) + ' Category: ' , item['value'])
                if ('Item' in url):
                    print('URL: ', url['Item']['value'])
                else:
                    print('Not Found')

# Make connections to Dynamo
dynamo_labels = Dynamo.dynamoStorage('Labels', sortKey=True)
dynamo_images = Dynamo.dynamoStorage('Images')

# Process Logic.
argv = sys.argv
argv.remove('queryDynamo.py')
getImages(argv)