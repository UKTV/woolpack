class Stack(object):
    """
    A light abstraction which enables us to build entire stacks.
    """

    def __init__(self, name=None):
        self.ec2 = []
        self.rds = []
        self.name = name

    def build(self):
        """ Calls the build method on each item
        to create the initial stack.
        """
        # When all is done, return True plus list of instances.
        created = [rds_inst.build() for rds_inst in self.rds
            if rds_inst.created is False]
        # register ec2 instances with ELB last.
        return created
