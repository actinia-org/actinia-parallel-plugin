#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2022 mundialis GmbH & Co. KG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Parallel processing
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"


import sys
import traceback
import pickle

from actinia_core.processing.actinia_processing.ephemeral.\
    persistent_processing import PersistentProcessing
from actinia_core.core.common.exceptions \
    import AsyncProcessError, AsyncProcessTermination
from actinia_core.core.common.exceptions import AsyncProcessTimeLimit
from actinia_core.models.response_models \
    import ExceptionTracebackModel

from actinia_parallel_plugin.core.batches import (
    checkProcessingBlockFinished,
    # createBatchResponseDict,
    getJobsByBatchId,
    startProcessingBlock,
)
from actinia_parallel_plugin.core.jobs import updateJob


class ParallelPersistentProcessing(PersistentProcessing):

    def __init__(self, rdc, batch_id, processing_block, jobid,
                 user, request_url, post_url, endpoint, method, path,
                 base_status_url):
        super(ParallelPersistentProcessing, self).__init__(rdc)
        self.batch_id = batch_id
        self.processing_block = processing_block
        self.jobid = jobid
        self.post_url = post_url
        self.user = user
        self.request_url = request_url
        self.post_url = post_url
        self.endpoint = endpoint
        self.method = method
        self.path = path
        self.base_status_url = base_status_url

    # def _execute(self, process_chain, skip_permission_check=False):
    def _execute(self, skip_permission_check=False):
        """Overwrite this function in subclasses.

        This function will be executed by the run() function

        - Setup logger and credentials
        - Analyse the process chain
        - Create the temporal database
        - Initialize the GRASS environment and create the temporary mapset
        - Run the modules
        - Parse the stdout output of the modules and generate the module
          results

        Args:
            skip_permission_check (bool): If set True, the permission checks of
                                          module access and process num
                                          limits are not performed

        Raises:
            This method will raise an AsyncProcessError, AsyncProcessTimeLimit
            or AsyncProcessTermination

        """
        # Create the process chain
        if self.rdc.iteration is not None:
            process_list = \
                self._create_temporary_grass_environment_and_process_list_for_iteration(
                    skip_permission_check=skip_permission_check)
        else:
            process_list = self._create_temporary_grass_environment_and_process_list(
                skip_permission_check=skip_permission_check)

        # Run all executables
        self._execute_process_list(process_list=process_list)
        # Parse the module sdtout outputs and create the results
        self._parse_module_outputs()

    def run(self):
        """This function will run the processing and will catch and process
        any Exceptions that were raised while processing. Call this function
        to run the processing.

        You have to implement/overwrite two methods that are called here:

            * self._execute()
            * self._final_cleanup()

            e_type, e_value, e_traceback = sys.exc_info()
            message = [e.__class__, e_type, e_value, traceback.format_tb(
                e_traceback)]
            message = pprint.pformat(message)
        """
        try:
            # Run the _execute function that does all the work
            self._execute()
        except AsyncProcessTermination as e:
            self.run_state = {"terminated": str(e)}
        except AsyncProcessTimeLimit as e:
            self.run_state = {"time limit exceeded": str(e)}
        except AsyncProcessError as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type)
            )
            self.run_state = {"error": str(e), "exception": model}
        except KeyboardInterrupt as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type)
            )
            self.run_state = {"error": str(e), "exception": model}
        except Exception as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type)
            )
            self.run_state = {"error": str(e), "exception": model}
        finally:
            try:
                # Call the final cleanup, before sending the status messages
                self._final_cleanup()
            except Exception as e:
                e_type, e_value, e_tb = sys.exc_info()
                model = ExceptionTracebackModel(
                    message=str(e_value),
                    traceback=traceback.format_tb(e_tb),
                    type=str(e_type)
                )
                self.run_state = {"error": str(e), "exception": model}
            # After all processing finished, send the final status
            if "success" in self.run_state:
                self._send_resource_finished(message=self.finish_message,
                                             results=self.module_results)
            elif "terminated" in self.run_state:
                # Send an error message if an exception was raised
                self._send_resource_terminated(
                    message=self.run_state["terminated"])
            elif "time limit exceeded" in self.run_state:
                self._send_resource_time_limit_exceeded(
                    message=self.run_state["time limit exceeded"])
            elif "error" in self.run_state:
                # Send an error message if an exception was raised
                self._send_resource_error(
                    message=self.run_state["error"],
                    exception=self.run_state["exception"])
            else:
                self._send_resource_error(message="Unknown error")
            self._update_and_check_batch_jobs()

    def _update_and_check_batch_jobs(self):
        """Checks batch jobs and starts new batch block if the current block
        is successfully finished.
        """

        # update job to finished
        resource_id = self.resource_id
        response_data = self.resource_logger.get(
            self.user_id, self.resource_id)
        _, response_model = pickle.loads(response_data)
        updateJob(resource_id, response_model, self.jobid)

        if "finished" == response_model["status"]:
            jobs_from_batch = getJobsByBatchId(
                self.batch_id,
                "persistent"
            )
            all_blocks = [
                job["processing_block"] for job in jobs_from_batch]
            block = int(self.processing_block)
            block_done = checkProcessingBlockFinished(
                jobs_from_batch, block)
            if block_done is True and block < max(all_blocks):
                next_block = block + 1
                startProcessingBlock(
                    jobs_from_batch,
                    next_block,
                    self.batch_id,
                    self.location_name,
                    self.mapset_name,
                    self.user,
                    self.request_url,
                    self.post_url,
                    self.endpoint,
                    self.method,
                    self.path,
                    self.base_status_url,
                    "persistent"
                )

        elif (response_model["status"] == "error" or
                response_model["status"] == "terminated"):
            # In this case, nothing happens and the next block is not
            # started.
            pass


def start_job(*args):
    processing = ParallelPersistentProcessing(*args)
    processing.run()
