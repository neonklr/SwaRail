from SwaRail import constants
from SwaRail.Frontend.Components.tracks import Track_Circuit
from SwaRail.Frontend.Components.signals import Signal
from SwaRail.Frontend.Components.stations import Station
from ursina import Vec3


class MapParser:
    map_data = None

    TRACK_CIRCUIT_ID_COUNTER = 1
    PREV_CONNECTION = None
    CURR_TRACK_CIRCUIT = None


    @classmethod
    def parse(cls, map_name):
        
        # reading file data
        with open(constants.MAP_PATH(map_name), 'r') as map_file:
            cls.map_data = map_file.read().split('\n') # TODO :- convert path to absolute path

        # iterating through each line and parsing it
        for line_no, line in enumerate(cls.map_data):
            cls._parse_line(line, line_no)

        # logging a summary of database
        constants.logging.debug(constants.Database.summary())


    @classmethod
    def _parse_line(cls, line, Y_coordinate):

        # TODO :- make a new and clean parse_line function...
        # there is no need for a seperate details class ... just make object of class Track
        # and work on it

        for index, character in enumerate(line):
            # no need to handle space... it helps in addings offset between components on map

            # TODO :- try to calculate X_coordinate and Y_coordinate outside all functions
            # before hand for easy debugging and reducing redundancy
            if character == ' ':
                pass

            elif character in '-<>=':
                cls._update_curr_track_circuit(character, index, Y_coordinate)

            elif character in '+':
                cls._seperate_track_circuits(index, Y_coordinate)

            elif character in '\/X':
                # TODO See if this is even required or not... if the above TODO of _update_curr_track_circuit()
                # is resolved... then remove this too
                if cls.CURR_TRACK_CIRCUIT != None:
                    cls.CURR_TRACK_CIRCUIT.ending_pos.x += constants.CHARACTER_TO_LENGTH

            elif character in '0123456789':
                cls._add_new_signal(character, index, Y_coordinate)

            else:
                # else is a station with station code and its mapping in railmap file
                cls._add_station(character, index, Y_coordinate)


        # add any remaining component to the database
        if cls.CURR_TRACK_CIRCUIT != None:
            cls._end_curr_track_circuit()

        # if cls.CURR_CROSSOVER != None:
        #     cls._end_curr_crossover(is_right_starter=True)

        # resetting used variables
        cls.TRACK_CIRCUIT_ID_COUNTER = 1
        cls.PREV_CONNECTION = None


    # ---------------------------- classmethods to update track circuits ---------------------------- #


    @classmethod
    def _update_curr_track_circuit(cls, character, X_coordinate, Y_coordinate):
        if cls.CURR_TRACK_CIRCUIT == None:
            cls.CURR_TRACK_CIRCUIT = Track_Circuit()
            cls.CURR_TRACK_CIRCUIT.ID = f'TC-{Y_coordinate}-{cls.TRACK_CIRCUIT_ID_COUNTER}'
            cls.CURR_TRACK_CIRCUIT.direction = constants.CHARACTER_TO_DIRECTION[character]
            cls.CURR_TRACK_CIRCUIT.connections["left"] = None if cls.PREV_CONNECTION == None else cls.PREV_CONNECTION.ID
            cls.CURR_TRACK_CIRCUIT.starting_pos = Vec3(X_coordinate * constants.CHARACTER_TO_LENGTH, -constants.MAP_LINES_OFFSET * Y_coordinate, 0)
            cls.CURR_TRACK_CIRCUIT.ending_pos = Vec3(X_coordinate * constants.CHARACTER_TO_LENGTH, -constants.MAP_LINES_OFFSET * Y_coordinate, 0)

            cls.TRACK_CIRCUIT_ID_COUNTER += 1

        
        # TODO :- there is no need for this... since we can just use starting and final index 
        # to find starting and final position of the circuit track... but it isn't working
        # fid out why
        cls.CURR_TRACK_CIRCUIT.ending_pos.x += constants.CHARACTER_TO_LENGTH


    @classmethod
    def _seperate_track_circuits(cls, X_coordinate, Y_coordinate):
        if cls.CURR_TRACK_CIRCUIT == None: # no track circuit to seperate
            constants.logging.warn(f"Ignoring track circuit seperation request at line:{Y_coordinate+1} col:{X_coordinate+1} since its declared before track circuit and direction registration")
            return None

        cls.CURR_TRACK_CIRCUIT.ending_pos = Vec3(X_coordinate * constants.CHARACTER_TO_LENGTH, -constants.MAP_LINES_OFFSET * Y_coordinate, 0)
        cls.CURR_TRACK_CIRCUIT.ending_pos.x += constants.CHARACTER_TO_LENGTH
        cls._end_curr_track_circuit()


    @classmethod
    def _end_curr_track_circuit(cls):

        # adding this track circuit to main shared database of track circuits
        constants.Database.TRACK_CIRCUITS[cls.CURR_TRACK_CIRCUIT.ID] = cls.CURR_TRACK_CIRCUIT
        
        # finalize current object
        cls.CURR_TRACK_CIRCUIT.finalize()

        # updating class attributes
        cls.PREV_CONNECTION = cls.CURR_TRACK_CIRCUIT
        cls.CURR_TRACK_CIRCUIT = None



    # -------------------------------- classmethods to update signals -------------------------------- #


    @classmethod
    def _create_new_signal(cls, character, X_coordinate, Y_coordinate):
        
        # defining signal metadata
        signal_id = f"S-{Y_coordinate}-{X_coordinate}"
        signal_details = constants.NUMBER_TO_SIGNAL[character]
        signal_direction, signal_type = signal_details.split('-')

        if signal_direction == 'right':
            signal_position = Vec3(X_coordinate * constants.CHARACTER_TO_LENGTH, (-constants.MAP_LINES_OFFSET * Y_coordinate)  + constants.SIGNAL_OFFSET_FROM_TRACKS, 0)
        else:
            signal_position = Vec3(X_coordinate * constants.CHARACTER_TO_LENGTH, (-constants.MAP_LINES_OFFSET * Y_coordinate) - constants.SIGNAL_OFFSET_FROM_TRACKS, 0)
        
        
        # Making a new signal
        curr_signal = Signal()

        curr_signal.ID = signal_id
        curr_signal.parent_track_circuit_id = cls.CURR_TRACK_CIRCUIT.ID
        curr_signal.direction = signal_direction
        curr_signal.signal_type = signal_type
        curr_signal.position = signal_position


        return curr_signal


    @classmethod
    def _update_signal_infos(cls, signal_id, signal_direction, curr_signal):
        # updating info in main database
        constants.Database.SIGNALS[signal_id] = curr_signal

        
        # updating info in current track circuit
        if cls.CURR_TRACK_CIRCUIT.signals.get(signal_direction, False):
            cls.CURR_TRACK_CIRCUIT.signals[signal_direction].append(signal_id)
        else:
            cls.CURR_TRACK_CIRCUIT.signals[signal_direction] = [signal_id]


    @classmethod
    def _add_new_signal(cls, character, X_coordinate, Y_coordinate):

        if cls.CURR_TRACK_CIRCUIT == None:
            constants.logging.warn(f"Rejecting Signal at line:{Y_coordinate+1} col:{X_coordinate+1} since its declared before track circuit and direction registration")
            return None

        # TODO See if this is even required or not... if the above TODO of _update_curr_track_circuit()
        # is resolved... then remove this too
        cls.CURR_TRACK_CIRCUIT.ending_pos.x += constants.CHARACTER_TO_LENGTH

        # making a new signal
        curr_signal = cls._create_new_signal(character, X_coordinate, Y_coordinate)

        # update info of this signal everywhere
        cls._update_signal_infos(curr_signal.ID, curr_signal.direction, curr_signal)


    # ------------------------------ classmethods to update crossovers ------------------------------ #







    # ------------------------------- classmethods to update stations ------------------------------- #

    @classmethod
    def _create_new_station(cls, character):
        curr_station = Station()
        curr_station.ID = f"H-{character}-{cls.CURR_TRACK_CIRCUIT.ID}"
        curr_station.main_station_id = character
        curr_station.parent_track_circuit_id = cls.CURR_TRACK_CIRCUIT.ID

        return curr_station


    @classmethod
    def _update_station_infos(cls, curr_station):
        # adding current hault to database
        constants.Database.HAULTS[curr_station.ID] = curr_station

        # adding current hault to a station
        if constants.Database.STATIONS.get(curr_station.main_station_id, False):
            constants.Database.STATIONS[curr_station.main_station_id].append(curr_station.ID)
        else:
            constants.Database.STATIONS[curr_station.main_station_id] = [curr_station.ID]


    @classmethod
    def _add_station(cls, character, X_coordinate, Y_coordinate):
        
        if cls.CURR_TRACK_CIRCUIT == None:
            constants.logging.warn(f"Rejecting hault (station) request at line:{Y_coordinate+1} col:{X_coordinate+1} since its declared before track circuit and direction registration")
            return None

        
        # TODO See if this is even required or not... if the above TODO of _update_curr_track_circuit()
        # is resolved... then remove this too
        cls.CURR_TRACK_CIRCUIT.ending_pos.x += constants.CHARACTER_TO_LENGTH


        if cls.CURR_TRACK_CIRCUIT.hault_id != None:
            constants.logging.warn(f"Ignoring hault (station) request at line:{Y_coordinate+1} col:{X_coordinate+1} since the track circuit is already a haulting track")
            return None

        #creating new station
        curr_station = cls._create_new_station(character)

        # registering track circuit as a haulting section
        cls.CURR_TRACK_CIRCUIT.hault_id = curr_station.ID

        # update station infos
        cls._update_station_infos(curr_station)