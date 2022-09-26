from ursina import Entity, Mesh, Vec3, Text
from SwaRail.Frontend import constants

class TrackCircuit(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.ID = None
        self.starting_pos = None
        self.ending_pos = None
        self.connections = {'>': [], '<': []}
        self.direction = None
        self.color = None
        self.signals = {'<': [], '>': []}
        self.length = 0
        self.label = None

        for key, value in kwargs.items():
            self.__setattr__(key, value)


    def finalize(self):
        # order is important

        self.finalize_attributes()
        self.draw()

        self.finalize_order()


    def finalize_attributes(self):
        # setting color
        self.color = constants.TRACK_CIRCUIT_COLOR[self.direction]
        
        # setting length of track circuit in KMs
        line_length = self.ending_pos.x - self.starting_pos.x
        self.length = round(line_length * 100) / 1000


    def draw(self):
        # setting model of track_circuit
        self.model = Mesh(
            vertices=[self.starting_pos, self.ending_pos],
            colors=[self.color, self.color],
            mode='line', 
            thickness=constants.TRACK_CIRCUIT_THICKNESS
        )

    def _get_connections_sorting_key(self, component_id):
        component_details = component_id.split('-')
        id_prefix = component_details[0]
        key = None

        match id_prefix:
            case 'TC' : key = component_details[2]
            case 'CO' : 
                curr_y_coordinate = self.ID.split('-')[1]
                if curr_y_coordinate == component_details[1]: key = component_details[2]
                elif curr_y_coordinate == component_details[3]: key = component_details[4]

        return int(key)



    def finalize_order(self):
        # reversing the order of left direction signals
        self.signals['<'].reverse()

        # the > direction connections should be sorted in increasing order of index
        self.connections['>'].sort(key = lambda id: self._get_connections_sorting_key(id))

        # the < direction connections should be sorted in decreasing order of index
        self.connections['<'].sort(key = lambda id: self._get_connections_sorting_key(id), reverse=True)


    def _get_label_position(self):
        position = (self.starting_pos + self.ending_pos) / 2        
        position += constants.TRACK_CIRCUIT_LABEL_OFFSET

        return position


    def _create_label(self):
        
        self.label = Text(
            text = self.ID,
            parent = Entity(),
            color = constants.TRACK_CIRCUIT_LABEL_COLOR,
            position = self._get_label_position(),
            scale = constants.TRACK_CIRCUIT_LABEL_SIZE
        )


    def show_label(self):
        if self.label == None:
            self._create_label()

        self.label.visible = True


    def __str__(self):
        return f'''
        I Am A Track Circuit
        ID = {self.ID}, starting pos = {self.starting_pos}, ending pos = {self.ending_pos}, length = {self.length} KM,
        direction is {self.direction}, connections = {self.connections}, color = {self.color}
        '''

    def input(self, key):
        pass

    def update(self):
        pass