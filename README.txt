For issues please submit a ticket on GitHub.

***DEPENDENCIES***
To run this script succesfully, you will need:
-A Python interpreter (eg. Spyder)
-An e-mail archive in .MBOX format

Other files are required for Geolocation and NLP capabilities:

-A relational database for geolocating IP addresses (eg. MaxMind) stored in the same folder as the script.
-A list of Works of Art relating to your collection stored in the same folder as the script at 'bibliography.txt'

***INSTRUCTIONS***

The script will take you through a number of questions in order to generate the outputs that you need.

1. Copy and paste the file directory for the collection you'd like to process into the space provided.

2.Run the script

3. 'Name your collection...' for example, use the name of the depositor or a unique identifier. Hit enter to confirm.

4.'Would you like to geocode the IP addresses in this collection? Y or N?' Enter either Y or N and hit enter. Ensure your entry is upper case. This stage requires a MaxMind database to be stored locally in the same folder as this script.

5.'Would you like to generate a GDPR compliant csv file from your MBOX collection? Y or N?'Enter either Y or N and hit enter. Ensure your entry is upper case. The file will be created using your collection name given in stage 3 with the suffix 'GDPR Sheet'.

6.'Would you like to generate Gephi compliant Node and Edge sheets? Y or N?'Enter either Y or N and hit enter. Ensure your entry is upper case. The files will be created using your collection name given in stage 3 with the suffix Node Sheet' and 'Edges Sheet'.

7.'Do you wish to drop blank records? This is recommended when using these sheets in Gephi. Y or N?' Enter either Y or N and hit enter. Ensure your entry is upper case. Selecting Y here will result in records with blank entries in the following fields being dropped from the dataset: 'Sender', 'Receiver', 'Date Sent'. Records that do not conform with the UTC requirements in Gephi will also be dropped. The script will inform you of how many records are dropped. Manual comparison is possible if a GDPR sheet was created in stage 5.


